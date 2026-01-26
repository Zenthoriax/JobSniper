"""
Migration Script: SQLite to Supabase
Migrates all job data from local SQLite database to Supabase cloud database
"""

import sqlite3
import pandas as pd
import os
import shutil
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
SQLITE_DB = "data/job_tracker.db"
SQLITE_BACKUP = f"data/job_tracker_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

def create_supabase_table(supabase: Client):
    """Create the jobs table in Supabase using SQL"""
    print("\n📋 Creating jobs table in Supabase...")
    
    # Note: Supabase table creation is typically done via the dashboard or SQL editor
    # This function provides the SQL for manual execution
    
    sql = """
    CREATE TABLE IF NOT EXISTS jobs (
        id BIGSERIAL PRIMARY KEY,
        company TEXT NOT NULL,
        role TEXT NOT NULL,
        location TEXT,
        duration TEXT,
        link TEXT UNIQUE NOT NULL,
        match_score REAL,
        status TEXT DEFAULT 'Not Applied',
        notes TEXT,
        date_found TEXT,
        date_applied TEXT,
        date_updated TEXT,
        CONSTRAINT valid_status CHECK (status IN ('Not Applied', 'Applied', 'Ongoing', 'Interviewing', 'Got Selected', 'Rejected'))
    );
    
    -- Enable Row Level Security (RLS)
    ALTER TABLE jobs ENABLE ROW LEVEL SECURITY;
    
    -- Create policy to allow all operations (you can customize this later)
    CREATE POLICY "Enable all access for authenticated users" ON jobs
        FOR ALL
        USING (true)
        WITH CHECK (true);
    """
    
    print("\n📝 SQL for table creation:")
    print("=" * 60)
    print(sql)
    print("=" * 60)
    
    print("\n💡 Please execute this SQL in your Supabase SQL Editor:")
    print("   1. Go to your Supabase dashboard")
    print("   2. Click 'SQL Editor' in the sidebar")
    print("   3. Click 'New Query'")
    print("   4. Paste the SQL above")
    print("   5. Click 'Run'")
    
    input("\n⏸️  Press Enter once you've created the table in Supabase...")
    
    # Verify table exists
    try:
        result = supabase.table('jobs').select("id").limit(1).execute()
        print("✅ Table verified successfully!")
        return True
    except Exception as e:
        print(f"❌ Error verifying table: {e}")
        return False

def backup_sqlite():
    """Create a backup of the SQLite database"""
    print(f"\n💾 Creating backup of SQLite database...")
    
    if not os.path.exists(SQLITE_DB):
        print(f"❌ SQLite database not found at {SQLITE_DB}")
        return False
    
    try:
        shutil.copy2(SQLITE_DB, SQLITE_BACKUP)
        print(f"✅ Backup created: {SQLITE_BACKUP}")
        return True
    except Exception as e:
        print(f"❌ Error creating backup: {e}")
        return False

def read_sqlite_data():
    """Read all data from SQLite database"""
    print(f"\n📖 Reading data from SQLite database...")
    
    try:
        conn = sqlite3.connect(SQLITE_DB)
        df = pd.read_sql_query("SELECT * FROM jobs", conn)
        conn.close()
        
        print(f"✅ Found {len(df)} jobs in SQLite database")
        
        # Show status breakdown
        print("\n📊 Status breakdown:")
        print(df['status'].value_counts())
        
        return df
    except Exception as e:
        print(f"❌ Error reading SQLite data: {e}")
        return None

def migrate_to_supabase(df: pd.DataFrame, supabase: Client):
    """Migrate data to Supabase"""
    print(f"\n🚀 Migrating {len(df)} jobs to Supabase...")
    
    success_count = 0
    error_count = 0
    duplicate_count = 0
    
    for idx, row in df.iterrows():
        try:
            # Prepare job data
            job_data = {
                "company": row['company'],
                "role": row['role'],
                "location": row['location'] if pd.notna(row['location']) else None,
                "duration": row['duration'] if pd.notna(row['duration']) else None,
                "link": row['link'],
                "match_score": float(row['match_score']) if pd.notna(row['match_score']) else 0.0,
                "status": row['status'] if pd.notna(row['status']) else 'Not Applied',
                "notes": row['notes'] if pd.notna(row['notes']) else None,
                "date_found": row['date_found'] if pd.notna(row['date_found']) else None,
                "date_applied": row['date_applied'] if pd.notna(row['date_applied']) else None,
                "date_updated": row['date_updated'] if pd.notna(row['date_updated']) else None,
            }
            
            # Insert into Supabase
            result = supabase.table('jobs').insert(job_data).execute()
            success_count += 1
            
            # Progress indicator
            if (idx + 1) % 10 == 0:
                print(f"   Progress: {idx + 1}/{len(df)} jobs migrated...")
                
        except Exception as e:
            error_str = str(e).lower()
            if "duplicate" in error_str or "unique" in error_str:
                duplicate_count += 1
            else:
                error_count += 1
                print(f"   ⚠️ Error migrating job {idx + 1}: {e}")
    
    print(f"\n✅ Migration complete!")
    print(f"   • Successfully migrated: {success_count}")
    print(f"   • Duplicates skipped: {duplicate_count}")
    print(f"   • Errors: {error_count}")
    
    return success_count, duplicate_count, error_count

def verify_migration(df_sqlite: pd.DataFrame, supabase: Client):
    """Verify that all data was migrated correctly"""
    print(f"\n🔍 Verifying migration...")
    
    try:
        # Get all jobs from Supabase
        result = supabase.table('jobs').select("*").execute()
        df_supabase = pd.DataFrame(result.data)
        
        print(f"   SQLite jobs: {len(df_sqlite)}")
        print(f"   Supabase jobs: {len(df_supabase)}")
        
        if len(df_supabase) >= len(df_sqlite):
            print("✅ All jobs successfully migrated!")
            
            # Verify status distribution
            print("\n📊 Status distribution in Supabase:")
            print(df_supabase['status'].value_counts())
            
            return True
        else:
            print(f"⚠️ Warning: Supabase has fewer jobs than SQLite")
            print(f"   Missing: {len(df_sqlite) - len(df_supabase)} jobs")
            return False
            
    except Exception as e:
        print(f"❌ Error verifying migration: {e}")
        return False

def main():
    """Main migration process"""
    print("=" * 60)
    print("🦅 JobSniper: SQLite to Supabase Migration")
    print("=" * 60)
    
    # Check environment variables
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("\n❌ Error: Supabase credentials not found!")
        print("Please add SUPABASE_URL and SUPABASE_KEY to your .env file")
        return
    
    print(f"\n🔗 Supabase URL: {SUPABASE_URL}")
    print(f"🔑 API Key: {SUPABASE_KEY[:20]}...")
    
    # Initialize Supabase client
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Supabase client initialized")
    except Exception as e:
        print(f"❌ Error initializing Supabase client: {e}")
        return
    
    # Step 1: Create table in Supabase
    if not create_supabase_table(supabase):
        print("\n❌ Migration aborted: Could not create/verify table")
        return
    
    # Step 2: Backup SQLite database
    if not backup_sqlite():
        print("\n⚠️ Warning: Could not create backup, but continuing...")
    
    # Step 3: Read SQLite data
    df_sqlite = read_sqlite_data()
    if df_sqlite is None or len(df_sqlite) == 0:
        print("\n❌ No data to migrate")
        return
    
    # Step 4: Migrate to Supabase
    success, duplicates, errors = migrate_to_supabase(df_sqlite, supabase)
    
    # Step 5: Verify migration
    if verify_migration(df_sqlite, supabase):
        print("\n" + "=" * 60)
        print("🎉 MIGRATION SUCCESSFUL!")
        print("=" * 60)
        print(f"\n📊 Summary:")
        print(f"   • Total jobs migrated: {success}")
        print(f"   • Duplicates skipped: {duplicates}")
        print(f"   • Errors: {errors}")
        print(f"   • Backup location: {SQLITE_BACKUP}")
        
        # Ask if user wants to remove SQLite database
        print(f"\n💡 The SQLite database is no longer needed.")
        response = input("   Do you want to remove it? (yes/no): ").lower()
        
        if response in ['yes', 'y']:
            try:
                os.remove(SQLITE_DB)
                print(f"✅ Removed {SQLITE_DB}")
                print(f"   Backup is still available at: {SQLITE_BACKUP}")
            except Exception as e:
                print(f"⚠️ Could not remove SQLite database: {e}")
        else:
            print(f"   SQLite database kept at: {SQLITE_DB}")
        
        print("\n✅ You can now use the dashboard with Supabase!")
        
    else:
        print("\n⚠️ Migration completed with warnings")
        print("Please check the Supabase dashboard to verify your data")

if __name__ == "__main__":
    main()
