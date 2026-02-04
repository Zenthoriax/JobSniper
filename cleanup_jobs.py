#!/usr/bin/env python3
"""
JobSniper Database Cleanup Script
Removes all job data from Supabase database and local files while preserving structure
"""

import os
import sys
import json
import pandas as pd
import argparse
from datetime import datetime
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from modules.db_manager import supabase, get_all_jobs, get_statistics
except ImportError:
    print("❌ Error: Could not import db_manager. Make sure you're in the JobSniper directory.")
    sys.exit(1)

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

# File paths
DATA_DIR = "data"
VERIFIED_JOBS_FILE = os.path.join(DATA_DIR, "verified", "verified_jobs.csv")
TRACKER_FILE = os.path.join(DATA_DIR, "Job_Application_Tracker.xlsx")
HISTORY_FILE = os.path.join(DATA_DIR, "history.json")
PROCESSED_FILE = os.path.join(DATA_DIR, "processed.json")
PROCESSED_METADATA_FILE = os.path.join(DATA_DIR, "processed_metadata.json")
BACKUP_DIR = os.path.join(DATA_DIR, "backups")

def print_header(text):
    """Print formatted header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(60)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

def print_success(text):
    """Print success message"""
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")

def print_warning(text):
    """Print warning message"""
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")

def print_error(text):
    """Print error message"""
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")

def print_info(text):
    """Print info message"""
    print(f"{Colors.OKCYAN}ℹ️  {text}{Colors.ENDC}")

def create_backup(backup_db=True, backup_local=True):
    """Create backup of current data before deletion"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    os.makedirs(BACKUP_DIR, exist_ok=True)
    
    backup_files = []
    
    try:
        if backup_db and supabase:
            # Backup database to JSON
            print_info("Creating database backup...")
            df = get_all_jobs()
            if len(df) > 0:
                backup_file = os.path.join(BACKUP_DIR, f"database_backup_{timestamp}.json")
                df.to_json(backup_file, orient='records', indent=2)
                backup_files.append(backup_file)
                print_success(f"Database backed up to: {backup_file}")
            else:
                print_info("Database is already empty, no backup needed")
        
        if backup_local:
            # Backup local files
            local_files = [
                VERIFIED_JOBS_FILE,
                TRACKER_FILE,
                HISTORY_FILE,
                PROCESSED_FILE,
                PROCESSED_METADATA_FILE
            ]
            
            for file_path in local_files:
                if os.path.exists(file_path):
                    file_name = os.path.basename(file_path)
                    backup_file = os.path.join(BACKUP_DIR, f"{file_name}.backup_{timestamp}")
                    
                    # Copy file
                    import shutil
                    shutil.copy2(file_path, backup_file)
                    backup_files.append(backup_file)
                    print_success(f"Backed up: {file_name}")
        
        if backup_files:
            print_success(f"\n✅ Created {len(backup_files)} backup file(s) in {BACKUP_DIR}")
        return True
    
    except Exception as e:
        print_error(f"Backup failed: {e}")
        return False

def get_current_stats():
    """Get current statistics before cleanup"""
    stats = {}
    
    # Database stats
    if supabase:
        try:
            db_stats = get_statistics()
            stats['database'] = {
                'total_jobs': db_stats.get('total_jobs', 0),
                'applied': db_stats.get('applied', 0),
                'not_applied': db_stats.get('not_applied', 0),
                'ongoing': db_stats.get('ongoing', 0),
                'interviewing': db_stats.get('interviewing', 0),
                'got_selected': db_stats.get('got_selected', 0),
                'rejected': db_stats.get('rejected', 0)
            }
        except Exception as e:
            print_warning(f"Could not get database stats: {e}")
            stats['database'] = {'total_jobs': 0}
    
    # Local file stats
    stats['local_files'] = {}
    
    if os.path.exists(VERIFIED_JOBS_FILE):
        try:
            df = pd.read_csv(VERIFIED_JOBS_FILE)
            stats['local_files']['verified_jobs'] = len(df)
        except:
            stats['local_files']['verified_jobs'] = 0
    
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, 'r') as f:
                history = json.load(f)
                stats['local_files']['history'] = len(history)
        except:
            stats['local_files']['history'] = 0
    
    if os.path.exists(PROCESSED_FILE):
        try:
            with open(PROCESSED_FILE, 'r') as f:
                processed = json.load(f)
                stats['local_files']['processed'] = len(processed)
        except:
            stats['local_files']['processed'] = 0
    
    return stats

def display_stats(stats):
    """Display statistics in a formatted way"""
    print_info("Current Data Summary:")
    print(f"\n{Colors.BOLD}Database:{Colors.ENDC}")
    if 'database' in stats:
        db = stats['database']
        print(f"  Total Jobs: {db.get('total_jobs', 0)}")
        if db.get('total_jobs', 0) > 0:
            print(f"  - Not Applied: {db.get('not_applied', 0)}")
            print(f"  - Applied: {db.get('applied', 0)}")
            print(f"  - Ongoing: {db.get('ongoing', 0)}")
            print(f"  - Interviewing: {db.get('interviewing', 0)}")
            print(f"  - Got Selected: {db.get('got_selected', 0)}")
            print(f"  - Rejected: {db.get('rejected', 0)}")
    
    print(f"\n{Colors.BOLD}Local Files:{Colors.ENDC}")
    if 'local_files' in stats:
        local = stats['local_files']
        print(f"  Verified Jobs: {local.get('verified_jobs', 0)}")
        print(f"  Email History: {local.get('history', 0)}")
        print(f"  Processed Jobs: {local.get('processed', 0)}")

def clean_database():
    """Delete all jobs from Supabase database (preserves table structure)"""
    if not supabase:
        print_error("Supabase client not initialized. Cannot clean database.")
        return False
    
    try:
        print_info("Deleting all jobs from Supabase database...")
        
        # Delete all records (this preserves the table structure)
        result = supabase.table('jobs').delete().neq('id', 0).execute()
        
        print_success("Database cleaned successfully! (Table structure preserved)")
        return True
    
    except Exception as e:
        print_error(f"Failed to clean database: {e}")
        return False

def clean_local_files():
    """Reset local data files to empty state (preserves file structure)"""
    try:
        print_info("Cleaning local data files...")
        
        # Clean verified_jobs.csv - keep file with headers only
        if os.path.exists(VERIFIED_JOBS_FILE):
            empty_df = pd.DataFrame(columns=[
                'Date Found', 'Company', 'Role', 'Location', 'Duration', 
                'Link', 'Match Score', 'Status'
            ])
            empty_df.to_csv(VERIFIED_JOBS_FILE, index=False)
            print_success("Cleaned: verified_jobs.csv")
        
        # Clean tracker Excel - keep file with headers only
        if os.path.exists(TRACKER_FILE):
            empty_df = pd.DataFrame(columns=[
                'Date Found', 'Company', 'Role', 'Location', 'Duration', 
                'Link', 'Match Score', 'Status'
            ])
            empty_df.to_excel(TRACKER_FILE, index=False)
            
            # Add dropdown validation
            from openpyxl import load_workbook
            from openpyxl.worksheet.datavalidation import DataValidation
            
            wb = load_workbook(TRACKER_FILE)
            ws = wb.active
            
            options = '"Not Applied,Applied,Ongoing,Interviewing,Got Selected,Rejected"'
            dv = DataValidation(type="list", formula1=options, allow_blank=True)
            dv.add('H2:H100')
            ws.add_data_validation(dv)
            
            wb.save(TRACKER_FILE)
            print_success("Cleaned: Job_Application_Tracker.xlsx")
        
        # Clean JSON files - reset to empty arrays/objects
        json_files = [
            (HISTORY_FILE, []),
            (PROCESSED_FILE, []),
            (PROCESSED_METADATA_FILE, {})
        ]
        
        for file_path, empty_content in json_files:
            if os.path.exists(file_path):
                with open(file_path, 'w') as f:
                    json.dump(empty_content, f, indent=2)
                print_success(f"Cleaned: {os.path.basename(file_path)}")
        
        print_success("\n✅ All local files cleaned! (File structure preserved)")
        return True
    
    except Exception as e:
        print_error(f"Failed to clean local files: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(
        description='Clean JobSniper database and local files (data only, structure preserved)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cleanup_jobs.py --all              # Clean everything with backup
  python cleanup_jobs.py --database-only    # Clean only database
  python cleanup_jobs.py --local-only       # Clean only local files
  python cleanup_jobs.py --all --no-backup  # Clean without backup
  python cleanup_jobs.py --all --force      # Clean without confirmation
        """
    )
    
    parser.add_argument('--database-only', action='store_true',
                        help='Clean only Supabase database')
    parser.add_argument('--local-only', action='store_true',
                        help='Clean only local files')
    parser.add_argument('--all', action='store_true',
                        help='Clean both database and local files (default)')
    parser.add_argument('--no-backup', action='store_true',
                        help='Skip backup creation')
    parser.add_argument('--force', action='store_true',
                        help='Skip confirmation prompts')
    
    args = parser.parse_args()
    
    # Default to --all if no specific option is chosen
    if not args.database_only and not args.local_only:
        args.all = True
    
    # Determine what to clean
    clean_db = args.database_only or args.all
    clean_local = args.local_only or args.all
    
    # Print header
    print_header("JobSniper Data Cleanup Tool")
    
    # Get current stats
    print_info("Analyzing current data...")
    stats = get_current_stats()
    display_stats(stats)
    
    # Check if there's anything to clean
    total_items = stats.get('database', {}).get('total_jobs', 0) + sum(stats.get('local_files', {}).values())
    
    if total_items == 0:
        print_warning("\n⚠️  No data found to clean. Everything is already empty!")
        return
    
    # Confirmation
    if not args.force:
        print(f"\n{Colors.WARNING}{Colors.BOLD}WARNING: This will permanently delete all job data!{Colors.ENDC}")
        print(f"{Colors.WARNING}Structure (database tables, file formats) will be preserved.{Colors.ENDC}")
        
        if not args.no_backup:
            print(f"{Colors.OKGREEN}A backup will be created before deletion.{Colors.ENDC}")
        
        response = input(f"\n{Colors.BOLD}Are you sure you want to proceed? (yes/no): {Colors.ENDC}").strip().lower()
        
        if response not in ['yes', 'y']:
            print_warning("Cleanup cancelled by user.")
            return
    
    # Create backup
    if not args.no_backup:
        print_header("Creating Backup")
        if not create_backup(backup_db=clean_db, backup_local=clean_local):
            if not args.force:
                response = input(f"\n{Colors.WARNING}Backup failed. Continue anyway? (yes/no): {Colors.ENDC}").strip().lower()
                if response not in ['yes', 'y']:
                    print_warning("Cleanup cancelled.")
                    return
    
    # Perform cleanup
    print_header("Cleaning Data")
    
    success = True
    
    if clean_db:
        if not clean_database():
            success = False
    
    if clean_local:
        if not clean_local_files():
            success = False
    
    # Final summary
    print_header("Cleanup Complete")
    
    if success:
        print_success("✅ All data has been successfully cleaned!")
        print_info("\nWhat was preserved:")
        print("  • Database table structure (jobs table still exists)")
        print("  • File structure (all files still exist with headers)")
        print("  • Configuration files")
        print("  • Scripts and code")
        
        if not args.no_backup:
            print_info(f"\n📦 Backups saved in: {BACKUP_DIR}")
        
        print(f"\n{Colors.OKGREEN}You can now start fresh with new job searches!{Colors.ENDC}")
    else:
        print_error("⚠️  Cleanup completed with some errors. Please check the messages above.")

if __name__ == "__main__":
    main()
