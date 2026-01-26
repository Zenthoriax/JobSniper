"""
Quick script to create the jobs table in Supabase
Run this before the migration
"""

from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

print("=" * 60)
print("🦅 JobSniper: Create Supabase Table")
print("=" * 60)

print(f"\n🔗 Connecting to Supabase...")
print(f"URL: {SUPABASE_URL}\n")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("📋 Please run the following SQL in your Supabase SQL Editor:")
print("=" * 60)

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

ALTER TABLE jobs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Enable all access" ON jobs
    FOR ALL
    USING (true)
    WITH CHECK (true);

CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);
CREATE INDEX IF NOT EXISTS idx_jobs_date_found ON jobs(date_found DESC);
CREATE INDEX IF NOT EXISTS idx_jobs_match_score ON jobs(match_score DESC);
"""

print(sql)
print("=" * 60)

print("\n📝 Steps to create the table:")
print("1. Go to https://supabase.com/dashboard")
print("2. Select your 'JobSniper' project")
print("3. Click 'SQL Editor' in the left sidebar")
print("4. Click 'New Query'")
print("5. Paste the SQL above")
print("6. Click 'Run' (or press Ctrl+Enter)")

input("\n⏸️  Press Enter once you've run the SQL in Supabase...")

# Verify table was created
print("\n🔍 Verifying table creation...")
try:
    result = supabase.table('jobs').select("id").limit(1).execute()
    print("✅ Table verified successfully!")
    print("\n🎉 You can now run the migration script:")
    print("   python3 migrate_to_supabase.py")
except Exception as e:
    print(f"❌ Table verification failed: {e}")
    print("\nPlease make sure you ran the SQL in Supabase dashboard")
