"""
Database Setup and Migration Script
Automatically creates database, tables, and migrates CSV data
"""

import sys
import os

# Add src to path
sys.path.insert(0, 'src/modules')

from db_connector import get_db
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def create_database_if_not_exists():
    """Create the jobsniper database if it doesn't exist"""
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    if not DATABASE_URL:
        print("❌ No DATABASE_URL found in .env")
        return False
    
    # Parse connection string to get database name
    # postgresql://user:pass@host:port/dbname
    parts = DATABASE_URL.split('/')
    db_name = parts[-1]
    base_url = '/'.join(parts[:-1]) + '/postgres'  # Connect to default postgres db
    
    try:
        # Connect to default postgres database
        conn = psycopg2.connect(base_url)
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'")
        exists = cursor.fetchone()
        
        if not exists:
            cursor.execute(f"CREATE DATABASE {db_name}")
            print(f"✅ Created database: {db_name}")
        else:
            print(f"✅ Database already exists: {db_name}")
        
        cursor.close()
        conn.close()
        return True
        
    except Exception as e:
        print(f"⚠️ Error creating database: {e}")
        print("💡 Make sure PostgreSQL is running and credentials are correct")
        return False

def main():
    """Main setup function"""
    print("🚀 JobSniper Database Setup")
    print("=" * 50)
    
    # Step 1: Create database
    print("\n📦 Step 1: Creating database...")
    if not create_database_if_not_exists():
        print("\n⚠️ Continuing anyway - database may already exist")
    
    # Step 2: Initialize tables
    print("\n📋 Step 2: Initializing tables...")
    db = get_db()
    
    if not db.use_database:
        print("❌ Database connection failed")
        print("📁 App will use CSV file storage as fallback")
        return
    
    # Step 3: Migrate CSV data
    print("\n📊 Step 3: Migrating CSV data...")
    db.migrate_csv_to_db()
    
    # Step 4: Verify
    print("\n✅ Step 4: Verifying setup...")
    df = db.get_verified_jobs()
    print(f"📈 Total jobs in database: {len(df)}")
    
    print("\n" + "=" * 50)
    print("🎉 Database setup complete!")
    print("💡 The app will now use PostgreSQL for data storage")

if __name__ == "__main__":
    main()
