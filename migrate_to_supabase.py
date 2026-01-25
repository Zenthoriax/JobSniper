"""
Migrate existing CSV data to Supabase
Run this once to upload all your existing jobs to the cloud database
"""

import sys
import pandas as pd
import os

sys.path.insert(0, 'src/modules')
from db_connector import get_db

def migrate_csv_to_supabase():
    """Migrate all CSV jobs to Supabase database"""
    
    print("🚀 Starting CSV to Supabase Migration")
    print("=" * 50)
    
    # Initialize database connection
    db = get_db()
    
    if not db.use_database:
        print("❌ Cannot connect to database")
        print("💡 Check your network connection and DATABASE_URL")
        return
    
    print("✅ Connected to Supabase database")
    
    # Check for CSV file
    csv_file = "data/verified/verified_jobs.csv"
    if not os.path.exists(csv_file):
        print(f"❌ CSV file not found: {csv_file}")
        return
    
    # Read CSV
    print(f"\n📂 Reading CSV file: {csv_file}")
    df = pd.read_csv(csv_file)
    print(f"✅ Found {len(df)} jobs in CSV")
    
    # Migrate each job
    print(f"\n📤 Uploading to Supabase...")
    migrated = 0
    skipped = 0
    
    for idx, row in df.iterrows():
        job_data = {
            'job_url': row.get('job_url'),
            'title': row.get('title'),
            'company': row.get('company'),
            'location': row.get('location'),
            'description': row.get('description'),
            'date_posted': row.get('date_posted'),
            'relevance_score': row.get('relevance_score'),
            'match_reason': row.get('match_reason'),
            'duration': row.get('duration'),
            'work_mode': row.get('work_mode'),
            'site': row.get('site')
        }
        
        if db.insert_verified_job(job_data):
            migrated += 1
            if migrated % 10 == 0:
                print(f"  ✅ Migrated {migrated} jobs...")
        else:
            skipped += 1
    
    print(f"\n" + "=" * 50)
    print(f"🎉 Migration Complete!")
    print(f"✅ Migrated: {migrated} jobs")
    print(f"⏭️  Skipped: {skipped} jobs (duplicates)")
    print(f"📊 Total in database: {migrated}")
    print("=" * 50)
    
    # Verify
    print(f"\n🔍 Verifying migration...")
    db_jobs = db.get_verified_jobs()
    print(f"✅ Database now has {len(db_jobs)} jobs")
    
    if len(db_jobs) > 0:
        print(f"\n📋 Sample job:")
        sample = db_jobs.iloc[0]
        print(f"  Title: {sample.get('title')}")
        print(f"  Company: {sample.get('company')}")
        print(f"  Score: {sample.get('relevance_score')}")

if __name__ == "__main__":
    migrate_csv_to_supabase()
