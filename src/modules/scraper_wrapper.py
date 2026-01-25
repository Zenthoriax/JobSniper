"""
Simple wrapper to integrate background scraper with existing dashboard
This allows gradual migration without rewriting the entire scraper control section
"""

import subprocess
import sys
import os

def run_scraper_background():
    """
    Start scraper in true background mode (detached from dashboard)
    Returns: dict with success status and PID
    """
    try:
        python_exe = sys.executable
        log_file = "data/scraper_live.log"
        pid_file = "data/scraper.pid"
        
        os.makedirs("data", exist_ok=True)
        
        # Clear old log
        if os.path.exists(log_file):
            os.remove(log_file)
        
        # Start detached process
        with open(log_file, 'w') as log_f:
            process = subprocess.Popen(
                [python_exe, "-u", "src/main.py"],
                stdout=log_f,
                stderr=subprocess.STDOUT,
                stdin=subprocess.DEVNULL,
                start_new_session=True,  # Detach completely
                cwd=os.getcwd()
            )
        
        # Save PID
        with open(pid_file, 'w') as f:
            f.write(str(process.pid))
        
        return {
            "success": True,
            "pid": process.pid,
            "message": "Scraper running in background"
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }
