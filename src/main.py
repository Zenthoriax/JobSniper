import sys
import os
import time
import json
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from modules.scraper import run_extraction
from modules.auditor import run_auditor
from modules.notifier import run_notifier
from modules.tracker import update_excel_tracker

# Load settings to match Notifier logic
HISTORY_FILE = os.path.join("data", "history.json")
# Lowered to 55 to work with enhanced local scoring
MIN_MATCH_SCORE = 55 

def load_history():
    if not os.path.exists(HISTORY_FILE): return []
    try:
        with open(HISTORY_FILE, 'r') as f: return json.load(f)
    except: return []

def main():
    start_time = time.time()
    print("==========================================")
    print("   🦅 JobSniper: Autonomous Hunter v2.0   ")
    print("==========================================")
    
    # 1. HUNT
    run_extraction()
    
    # 2. AUDIT
    run_auditor()
    
    # 3. TRACK & NOTIFY PREP
    # We need to identify exactly which jobs are "New" and "Good"
    verified_path = os.path.join("data", "verified", "verified_jobs.csv")
    
    if os.path.exists(verified_path):
        df = pd.read_csv(verified_path)
        
        if not df.empty:
            # A. Filter by Score (Same as Notifier)
            df['relevance_score'] = pd.to_numeric(df['relevance_score'], errors='coerce').fillna(0)
            high_quality_df = df[df['relevance_score'] >= MIN_MATCH_SCORE]
            
            # B. Filter by History (Only "New" jobs)
            history = load_history()
            jobs_to_email = high_quality_df[~high_quality_df['job_url'].isin(history)]
            
            # C. Update Tracker ONLY with these specific jobs
            if not jobs_to_email.empty:
                update_excel_tracker(jobs_to_email)
            else:
                print("ℹ️ No new jobs to add to tracker.")

    # 4. REPORT (Emails & Updates History)
    run_notifier()

    elapsed = round(time.time() - start_time, 2)
    print(f"\n✅ Mission Complete. Total execution time: {elapsed}s")

if __name__ == "__main__":
    main()