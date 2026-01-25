"""
Background Scraper Manager
Handles running the scraper in a detached background process
Provides progress tracking and process management
"""

import os
import sys
import json
import subprocess
import psutil
import time
from datetime import datetime
from pathlib import Path

# File paths
PROGRESS_FILE = "data/scraper_progress.json"
PID_FILE = "data/scraper.pid"
LOG_FILE = "data/scraper_live.log"
BACKUP_DIR = "data/backups"

# Backup file paths
VERIFIED_JOBS_FILE = "data/verified/verified_jobs.csv"
RAW_JOBS_FILE = "data/raw/jobs_latest.csv"
HISTORY_FILE = "data/history.json"
PROCESSED_FILE = "data/processed.json"

class BackgroundScraper:
    """Manages background scraper process"""
    
    def __init__(self):
        self.progress_file = PROGRESS_FILE
        self.pid_file = PID_FILE
        self.log_file = LOG_FILE
        os.makedirs("data", exist_ok=True)
    
    def is_running(self):
        """Check if scraper is currently running"""
        if not os.path.exists(self.pid_file):
            return False
        
        try:
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            # Check if process exists and is running
            if psutil.pid_exists(pid):
                process = psutil.Process(pid)
                # Check if it's actually our scraper process
                if process.is_running() and process.status() != psutil.STATUS_ZOMBIE:
                    return True
            
            # Process doesn't exist, clean up PID file
            self.cleanup()
            return False
        except (ValueError, psutil.NoSuchProcess, psutil.AccessDenied):
            self.cleanup()
            return False
    
    def start(self):
        """Start scraper in background with automatic backup"""
        if self.is_running():
            return {
                "success": False,
                "error": "Scraper is already running"
            }
        
        try:
            # Clean up old files
            self.cleanup()
            
            # Create backup before starting
            backup_path = self._create_backup()
            
            # Initialize progress file
            self._update_progress({
                "status": "starting",
                "phase": "initialization",
                "jobs_scraped": 0,
                "jobs_verified": 0,
                "high_score_jobs": 0,
                "start_time": datetime.now().isoformat(),
                "last_update": datetime.now().isoformat(),
                "backup_path": backup_path,
                "error": None
            })
            
            # Get Python executable
            python_exe = sys.executable
            
            # Start scraper as detached background process
            # Use nohup-like approach for true background execution
            with open(self.log_file, 'w') as log_f:
                process = subprocess.Popen(
                    [python_exe, "-u", "src/main.py"],
                    stdout=log_f,
                    stderr=subprocess.STDOUT,
                    stdin=subprocess.DEVNULL,
                    start_new_session=True,  # Detach from parent
                    cwd=os.getcwd()
                )
            
            # Save PID
            with open(self.pid_file, 'w') as f:
                f.write(str(process.pid))
            
            return {
                "success": True,
                "pid": process.pid,
                "backup_path": backup_path,
                "message": "Scraper started in background (backup created)"
            }
        
        except Exception as e:
            self._update_progress({
                "status": "error",
                "error": str(e),
                "last_update": datetime.now().isoformat()
            })
            return {
                "success": False,
                "error": str(e)
            }
    
    def stop(self, rollback=False):
        """Stop running scraper with optional rollback
        
        Args:
            rollback: If True, restore data from backup created at start
        """
        if not self.is_running():
            return {
                "success": False,
                "error": "No scraper is running"
            }
        
        try:
            # Get backup path before stopping
            progress = self.get_progress()
            backup_path = progress.get("backup_path")
            
            # Stop the process
            with open(self.pid_file, 'r') as f:
                pid = int(f.read().strip())
            
            process = psutil.Process(pid)
            
            # Graceful termination
            process.terminate()
            
            # Wait up to 10 seconds for graceful shutdown
            try:
                process.wait(timeout=10)
            except psutil.TimeoutExpired:
                # Force kill if it doesn't terminate
                process.kill()
            
            # Perform rollback if requested
            rollback_success = False
            if rollback and backup_path:
                rollback_success = self._restore_backup(backup_path)
            
            # Update progress
            self._update_progress({
                "status": "cancelled",
                "rollback_performed": rollback,
                "rollback_success": rollback_success,
                "last_update": datetime.now().isoformat()
            })
            
            self.cleanup()
            
            message = "Scraper stopped"
            if rollback:
                if rollback_success:
                    message += " and data rolled back successfully"
                else:
                    message += " but rollback failed (backup may not exist)"
            
            return {
                "success": True,
                "rollback_performed": rollback,
                "rollback_success": rollback_success,
                "message": message
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_progress(self):
        """Get current scraper progress"""
        if not os.path.exists(self.progress_file):
            return {
                "status": "idle",
                "phase": None,
                "jobs_scraped": 0,
                "jobs_verified": 0,
                "high_score_jobs": 0
            }
        
        try:
            with open(self.progress_file, 'r') as f:
                progress = json.load(f)
            
            # Update with real-time data from files
            if progress.get("status") == "running":
                progress = self._enrich_progress(progress)
            
            return progress
        except:
            return {
                "status": "error",
                "error": "Failed to read progress"
            }
    
    def get_logs(self, tail_lines=50):
        """Get scraper logs"""
        if not os.path.exists(self.log_file):
            return ""
        
        try:
            with open(self.log_file, 'r') as f:
                lines = f.readlines()
                return "".join(lines[-tail_lines:])
        except:
            return ""
    
    def cleanup(self):
        """Clean up PID and temporary files"""
        for file in [self.pid_file]:
            if os.path.exists(file):
                try:
                    os.remove(file)
                except:
                    pass
    
    def _update_progress(self, data):
        """Update progress file"""
        try:
            # Load existing progress
            existing = {}
            if os.path.exists(self.progress_file):
                with open(self.progress_file, 'r') as f:
                    existing = json.load(f)
            
            # Merge with new data
            existing.update(data)
            
            # Save
            with open(self.progress_file, 'w') as f:
                json.dump(existing, f, indent=2)
        except:
            pass
    
    def _enrich_progress(self, progress):
        """Enrich progress with real-time file data"""
        # Check jobs_latest.csv for scraped jobs
        jobs_file = "data/raw/jobs_latest.csv"
        if os.path.exists(jobs_file):
            try:
                import pandas as pd
                df = pd.read_csv(jobs_file)
                progress["jobs_scraped"] = len(df)
            except:
                pass
        
        # Check verified_jobs.csv for verified jobs
        verified_file = "data/verified/verified_jobs.csv"
        if os.path.exists(verified_file):
            try:
                import pandas as pd
                df = pd.read_csv(verified_file)
                progress["jobs_verified"] = len(df)
                
                # Count high score jobs
                df['relevance_score'] = pd.to_numeric(df['relevance_score'], errors='coerce').fillna(0)
                progress["high_score_jobs"] = len(df[df['relevance_score'] >= 75])
            except:
                pass
        
        progress["last_update"] = datetime.now().isoformat()
        return progress
    
    def _create_backup(self):
        """Create backup of current data files before scraping
        
        Returns:
            str: Path to backup directory
        """
        import shutil
        
        # Create backup directory with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(BACKUP_DIR, f"backup_{timestamp}")
        os.makedirs(backup_path, exist_ok=True)
        
        # Files to backup
        files_to_backup = [
            (VERIFIED_JOBS_FILE, "verified_jobs.csv"),
            (RAW_JOBS_FILE, "jobs_latest.csv"),
            (HISTORY_FILE, "history.json"),
            (PROCESSED_FILE, "processed.json")
        ]
        
        backed_up_count = 0
        for source, dest_name in files_to_backup:
            if os.path.exists(source):
                try:
                    dest = os.path.join(backup_path, dest_name)
                    shutil.copy2(source, dest)
                    backed_up_count += 1
                except Exception as e:
                    print(f"Warning: Failed to backup {source}: {e}")
        
        # Save backup metadata
        metadata = {
            "timestamp": timestamp,
            "files_backed_up": backed_up_count,
            "created_at": datetime.now().isoformat()
        }
        
        with open(os.path.join(backup_path, "metadata.json"), 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return backup_path
    
    def _restore_backup(self, backup_path):
        """Restore data from backup
        
        Args:
            backup_path: Path to backup directory
            
        Returns:
            bool: True if restore successful
        """
        import shutil
        
        if not os.path.exists(backup_path):
            return False
        
        try:
            # Files to restore
            files_to_restore = [
                ("verified_jobs.csv", VERIFIED_JOBS_FILE),
                ("jobs_latest.csv", RAW_JOBS_FILE),
                ("history.json", HISTORY_FILE),
                ("processed.json", PROCESSED_FILE)
            ]
            
            restored_count = 0
            for source_name, dest in files_to_restore:
                source = os.path.join(backup_path, source_name)
                if os.path.exists(source):
                    try:
                        # Ensure destination directory exists
                        os.makedirs(os.path.dirname(dest), exist_ok=True)
                        shutil.copy2(source, dest)
                        restored_count += 1
                    except Exception as e:
                        print(f"Warning: Failed to restore {source_name}: {e}")
            
            return restored_count > 0
        
        except Exception as e:
            print(f"Error during restore: {e}")
            return False
    
    def list_backups(self):
        """List all available backups
        
        Returns:
            list: List of backup info dicts
        """
        if not os.path.exists(BACKUP_DIR):
            return []
        
        backups = []
        for backup_name in os.listdir(BACKUP_DIR):
            backup_path = os.path.join(BACKUP_DIR, backup_name)
            if os.path.isdir(backup_path):
                metadata_file = os.path.join(backup_path, "metadata.json")
                if os.path.exists(metadata_file):
                    try:
                        with open(metadata_file, 'r') as f:
                            metadata = json.load(f)
                        metadata["path"] = backup_path
                        metadata["name"] = backup_name
                        backups.append(metadata)
                    except:
                        pass
        
        # Sort by timestamp (newest first)
        backups.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return backups


# Singleton instance
_scraper_instance = None

def get_scraper():
    """Get singleton scraper instance"""
    global _scraper_instance
    if _scraper_instance is None:
        _scraper_instance = BackgroundScraper()
    return _scraper_instance
