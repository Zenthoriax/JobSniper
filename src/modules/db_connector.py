"""
PostgreSQL Database Connector
Handles database connections with automatic initialization and fallback to CSV
"""

import os
import psycopg2
from psycopg2 import pool, sql
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import pandas as pd
from datetime import datetime

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

class DatabaseConnector:
    """PostgreSQL connection manager with auto-initialization"""
    
    def __init__(self):
        self.connection_pool = None
        self.use_database = False
        
        if DATABASE_URL:
            try:
                self._initialize_pool()
                self._initialize_database()
                self.use_database = True
                print("✅ Connected to PostgreSQL database")
            except Exception as e:
                print(f"⚠️ Database connection failed: {e}")
                print("📁 Falling back to CSV file storage")
                self.use_database = False
        else:
            print("📁 No DATABASE_URL found, using CSV file storage")
    
    def _initialize_pool(self):
        """Create connection pool"""
        self.connection_pool = psycopg2.pool.SimpleConnectionPool(
            1, 10,  # min and max connections
            DATABASE_URL
        )
    
    def _initialize_database(self):
        """Auto-create database and tables if they don't exist"""
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            
            # Create verified_jobs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS verified_jobs (
                    id SERIAL PRIMARY KEY,
                    job_url TEXT UNIQUE NOT NULL,
                    title TEXT,
                    company TEXT,
                    location TEXT,
                    description TEXT,
                    date_posted TIMESTAMP,
                    relevance_score INTEGER,
                    match_reason TEXT,
                    duration TEXT,
                    work_mode TEXT,
                    site TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create raw_jobs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS raw_jobs (
                    id SERIAL PRIMARY KEY,
                    job_url TEXT UNIQUE NOT NULL,
                    title TEXT,
                    company TEXT,
                    location TEXT,
                    description TEXT,
                    date_posted TIMESTAMP,
                    site TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create processed_jobs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS processed_jobs (
                    id SERIAL PRIMARY KEY,
                    job_url TEXT UNIQUE NOT NULL,
                    processed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create email_history table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS email_history (
                    id SERIAL PRIMARY KEY,
                    job_url TEXT NOT NULL,
                    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT
                )
            """)
            
            # Create scraper_runs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS scraper_runs (
                    id SERIAL PRIMARY KEY,
                    start_time TIMESTAMP,
                    end_time TIMESTAMP,
                    status TEXT,
                    jobs_scraped INTEGER DEFAULT 0,
                    jobs_verified INTEGER DEFAULT 0,
                    high_score_jobs INTEGER DEFAULT 0,
                    backup_path TEXT,
                    error_message TEXT
                )
            """)
            
            conn.commit()
            print("✅ Database tables initialized")
            
        except Exception as e:
            conn.rollback()
            print(f"⚠️ Database initialization error: {e}")
            raise
        finally:
            self.return_connection(conn)
    
    def get_connection(self):
        """Get a connection from the pool"""
        if self.connection_pool:
            return self.connection_pool.getconn()
        return None
    
    def return_connection(self, conn):
        """Return connection to pool"""
        if self.connection_pool and conn:
            self.connection_pool.putconn(conn)
    
    def execute_query(self, query, params=None, fetch=False):
        """Execute a query and optionally fetch results"""
        if not self.use_database:
            return None
        
        conn = self.get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query, params)
            
            if fetch:
                result = cursor.fetchall()
                return result
            else:
                conn.commit()
                return cursor.rowcount
        except Exception as e:
            conn.rollback()
            print(f"Query error: {e}")
            return None
        finally:
            self.return_connection(conn)
    
    def insert_verified_job(self, job_data):
        """Insert or update a verified job"""
        if not self.use_database:
            return False
        
        query = """
            INSERT INTO verified_jobs 
            (job_url, title, company, location, description, date_posted, 
             relevance_score, match_reason, duration, work_mode, site)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (job_url) 
            DO UPDATE SET
                relevance_score = EXCLUDED.relevance_score,
                match_reason = EXCLUDED.match_reason,
                duration = EXCLUDED.duration,
                work_mode = EXCLUDED.work_mode,
                updated_at = CURRENT_TIMESTAMP
        """
        
        params = (
            job_data.get('job_url'),
            job_data.get('title'),
            job_data.get('company'),
            job_data.get('location'),
            job_data.get('description'),
            job_data.get('date_posted'),
            job_data.get('relevance_score'),
            job_data.get('match_reason'),
            job_data.get('duration'),
            job_data.get('work_mode'),
            job_data.get('site')
        )
        
        return self.execute_query(query, params) is not None
    
    def get_verified_jobs(self):
        """Get all verified jobs as DataFrame"""
        if not self.use_database:
            # Fallback to CSV
            csv_file = "data/verified/verified_jobs.csv"
            if os.path.exists(csv_file):
                return pd.read_csv(csv_file)
            return pd.DataFrame()
        
        query = """
            SELECT job_url, title, company, location, description, 
                   date_posted, relevance_score, match_reason, 
                   duration, work_mode, site, created_at
            FROM verified_jobs
            ORDER BY relevance_score DESC, created_at DESC
        """
        
        results = self.execute_query(query, fetch=True)
        if results:
            return pd.DataFrame(results)
        return pd.DataFrame()
    
    def migrate_csv_to_db(self):
        """Migrate existing CSV data to PostgreSQL"""
        if not self.use_database:
            print("Database not available, skipping migration")
            return
        
        csv_file = "data/verified/verified_jobs.csv"
        if not os.path.exists(csv_file):
            print("No CSV file to migrate")
            return
        
        try:
            df = pd.read_csv(csv_file)
            migrated = 0
            
            for _, row in df.iterrows():
                job_data = row.to_dict()
                if self.insert_verified_job(job_data):
                    migrated += 1
            
            print(f"✅ Migrated {migrated} jobs from CSV to PostgreSQL")
        except Exception as e:
            print(f"⚠️ Migration error: {e}")
    
    def close(self):
        """Close all connections"""
        if self.connection_pool:
            self.connection_pool.closeall()


# Singleton instance
_db_instance = None

def get_db():
    """Get singleton database instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = DatabaseConnector()
    return _db_instance
