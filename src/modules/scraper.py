import pandas as pd
import time
import random
from jobspy import scrape_jobs
from config import settings
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_extraction():
    all_jobs = []
    
    print(f"🚀 Starting Extraction Engine (Multi-Location Mode)...")
    print(f"🎯 Sites: {settings.TARGET_SITES}")
    print(f"🌍 Locations: {settings.LOCATIONS}")
    
    # 1. Loop through SEARCH QUERIES
    for query in settings.SEARCH_QUERIES:
        print(f"\n🔎 Query: '{query}'")
        
        # 2. Loop through LOCATIONS (The Fix)
        for loc in settings.LOCATIONS:
            print(f"   📍 Checking {loc}...", end="")
            
            # 3. Loop through SITES
            for site in settings.TARGET_SITES:
                try:
                    # Random delay to be safe
                    time.sleep(random.uniform(2, 4))
                    
                    jobs = scrape_jobs(
                        site_name=[site],
                        search_term=query,
                        location=loc,  # <--- FIXED: Uses the loop variable, not [0]
                        results_wanted=settings.RESULTS_WANTED,
                        hours_old=settings.HOURS_OLD, 
                        country_ind=settings.COUNTRY, 
                    )
                    
                    if not jobs.empty:
                        # Clean empty descriptions immediately
                        jobs = jobs.dropna(subset=['description'])
                        jobs = jobs[jobs['description'].str.len() > 50]
                        
                        if not jobs.empty:
                            jobs['search_query'] = query
                            jobs['location_searched'] = loc
                            all_jobs.append(jobs)
                            print(f" [Found {len(jobs)} on {site}]", end="")
                            
                except Exception as e:
                    # Errors are expected on some site/location combos, just skip
                    continue
            print("") # New line after location is done

    # Combine and Deduplicate
    if all_jobs:
        master_df = pd.concat(all_jobs, ignore_index=True)
        
        # SMART DEDUPLICATION
        master_df['norm_company'] = master_df['company'].astype(str).str.lower().str.strip()
        master_df['norm_title'] = master_df['title'].astype(str).str.lower().str.strip()
        master_df['desc_len'] = master_df['description'].str.len()
        master_df = master_df.sort_values('desc_len', ascending=False)
        
        before_dedup = len(master_df)
        master_df = master_df.drop_duplicates(subset=['norm_company', 'norm_title'], keep='first')
        master_df = master_df.drop(columns=['norm_company', 'norm_title', 'desc_len'])
        
        dupes_removed = before_dedup - len(master_df)
        
        filename = f"{settings.DATA_DIR}/jobs_latest.csv"
        master_df.to_csv(filename, index=False)
        print(f"\n✨ Scrape Complete.")
        print(f"   - Raw Jobs Found: {before_dedup}")
        print(f"   - Duplicates Removed: {dupes_removed}")
        print(f"   - Unique Jobs Saved: {len(master_df)}")
        return master_df
    else:
        print("\n😔 No jobs found on any site/location.")
        return pd.DataFrame()