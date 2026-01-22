"""
Database Manager for JobSniper Application Tracker
Handles SQLite database operations and Excel synchronization
"""

import sqlite3
import pandas as pd
import os
from datetime import datetime
from typing import List, Dict, Optional

DB_FILE = "data/job_tracker.db"
EXCEL_FILE = "data/Job_Application_Tracker.xlsx"

# Status options
VALID_STATUSES = [
    "Not Applied",
    "Applied", 
    "Ongoing",
    "Interviewing",
    "Got Selected",
    "Rejected"
]

def init_db():
    """Initialize the SQLite database with the jobs table"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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
        )
    """)
    
    conn.commit()
    conn.close()
    print("✅ Database initialized")

def add_job(company: str, role: str, link: str, match_score: float, 
            location: str = None, duration: str = None) -> bool:
    """Add a new job to the database"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        date_found = datetime.now().strftime("%Y-%m-%d")
        
        cursor.execute("""
            INSERT INTO jobs (company, role, location, duration, link, match_score, 
                            status, date_found, date_updated)
            VALUES (?, ?, ?, ?, ?, ?, 'Not Applied', ?, ?)
        """, (company, role, location, duration, link, match_score, date_found, date_found))
        
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        # Job already exists (duplicate link)
        return False
    except Exception as e:
        print(f"Error adding job: {e}")
        return False

def get_all_jobs() -> pd.DataFrame:
    """Get all jobs from the database as a DataFrame"""
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM jobs ORDER BY date_found DESC, match_score DESC", conn)
    conn.close()
    return df

def get_jobs_by_status(status: str) -> pd.DataFrame:
    """Get jobs filtered by status"""
    conn = sqlite3.connect(DB_FILE)
    df = pd.read_sql_query("SELECT * FROM jobs WHERE status = ? ORDER BY date_found DESC", conn, params=(status,))
    conn.close()
    return df

def update_job_status(job_id: int, new_status: str) -> bool:
    """Update the status of a job"""
    if new_status not in VALID_STATUSES:
        return False
    
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        date_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # If status is "Applied", also set date_applied
        if new_status == "Applied":
            cursor.execute("""
                UPDATE jobs 
                SET status = ?, date_applied = ?, date_updated = ?
                WHERE id = ?
            """, (new_status, datetime.now().strftime("%Y-%m-%d"), date_updated, job_id))
        else:
            cursor.execute("""
                UPDATE jobs 
                SET status = ?, date_updated = ?
                WHERE id = ?
            """, (new_status, date_updated, job_id))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error updating status: {e}")
        return False

def update_job_notes(job_id: int, notes: str) -> bool:
    """Update notes for a job"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        date_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor.execute("""
            UPDATE jobs 
            SET notes = ?, date_updated = ?
            WHERE id = ?
        """, (notes, date_updated, job_id))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error updating notes: {e}")
        return False

def delete_job(job_id: int) -> bool:
    """Delete a job from the database"""
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM jobs WHERE id = ?", (job_id,))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"Error deleting job: {e}")
        return False

def get_statistics() -> Dict:
    """Get statistics about applications"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    stats = {}
    
    # Total jobs
    cursor.execute("SELECT COUNT(*) FROM jobs")
    stats['total_jobs'] = cursor.fetchone()[0]
    
    # Count by status
    for status in VALID_STATUSES:
        cursor.execute("SELECT COUNT(*) FROM jobs WHERE status = ?", (status,))
        stats[status.lower().replace(' ', '_')] = cursor.fetchone()[0]
    
    # Average match score
    cursor.execute("SELECT AVG(match_score) FROM jobs")
    avg_score = cursor.fetchone()[0]
    stats['avg_match_score'] = round(avg_score, 1) if avg_score else 0
    
    # Success rate (Got Selected / Applied)
    applied = stats['applied'] + stats['ongoing'] + stats['interviewing'] + stats['got_selected'] + stats['rejected']
    if applied > 0:
        stats['success_rate'] = round((stats['got_selected'] / applied) * 100, 1)
    else:
        stats['success_rate'] = 0
    
    conn.close()
    return stats

def sync_from_excel():
    """Import jobs from Excel to database (one-time migration)"""
    if not os.path.exists(EXCEL_FILE):
        print("No Excel file found to sync from")
        return
    
    try:
        df = pd.read_excel(EXCEL_FILE)
        
        # Map Excel columns to database columns
        for _, row in df.iterrows():
            add_job(
                company=row.get('Company', ''),
                role=row.get('Role', ''),
                link=row.get('Link', ''),
                match_score=row.get('Match Score', 0),
                location=row.get('Location', ''),
                duration=row.get('Duration', '')
            )
            
            # Update status if it exists
            if 'Status' in row and pd.notna(row['Status']):
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE jobs SET status = ? WHERE link = ?
                """, (row['Status'], row['Link']))
                conn.commit()
                conn.close()
        
        print(f"✅ Synced {len(df)} jobs from Excel to database")
    except Exception as e:
        print(f"Error syncing from Excel: {e}")

def sync_to_excel():
    """Export database to Excel (for compatibility)"""
    try:
        df = get_all_jobs()
        
        # Reorder and rename columns to match Excel format
        export_df = pd.DataFrame()
        export_df['Date Found'] = df['date_found']
        export_df['Company'] = df['company']
        export_df['Role'] = df['role']
        export_df['Location'] = df['location']
        export_df['Duration'] = df['duration']
        export_df['Link'] = df['link']
        export_df['Match Score'] = df['match_score']
        export_df['Status'] = df['status']
        
        export_df.to_excel(EXCEL_FILE, index=False)
        
        # Add dropdowns
        from openpyxl import load_workbook
        from openpyxl.worksheet.datavalidation import DataValidation
        
        wb = load_workbook(EXCEL_FILE)
        ws = wb.active
        
        options = '"Not Applied,Applied,Ongoing,Interviewing,Got Selected,Rejected"'
        dv = DataValidation(type="list", formula1=options, allow_blank=True)
        dv.add(f'H2:H{len(export_df) + 50}')
        ws.add_data_validation(dv)
        
        wb.save(EXCEL_FILE)
        print(f"✅ Synced {len(df)} jobs to Excel")
    except Exception as e:
        print(f"Error syncing to Excel: {e}")

# Initialize database on import
if not os.path.exists(DB_FILE):
    init_db()
    # If Excel exists, migrate data
    if os.path.exists(EXCEL_FILE):
        sync_from_excel()
