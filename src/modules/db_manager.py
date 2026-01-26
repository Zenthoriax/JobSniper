"""
Database Manager for JobSniper Application Tracker
Handles Supabase cloud database operations and Excel synchronization
"""

import pandas as pd
import os
from datetime import datetime
from typing import List, Dict, Optional
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Initialize Supabase client
supabase: Client = None
if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

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
    """Initialize the Supabase database with the jobs table"""
    if not supabase:
        raise Exception("Supabase client not initialized. Please set SUPABASE_URL and SUPABASE_KEY in .env file")
    
    # Note: Table creation should be done via Supabase dashboard or migration script
    # This function verifies the connection
    try:
        # Test connection by querying the table
        result = supabase.table('jobs').select("id").limit(1).execute()
        print("✅ Supabase database connection successful")
        return True
    except Exception as e:
        print(f"⚠️ Database connection error: {e}")
        print("💡 Make sure the 'jobs' table exists in Supabase")
        return False

def add_job(company: str, role: str, link: str, match_score: float, 
            location: str = None, duration: str = None) -> bool:
    """Add a new job to the database"""
    if not supabase:
        print("Error: Supabase client not initialized")
        return False
    
    try:
        date_found = datetime.now().strftime("%Y-%m-%d")
        
        job_data = {
            "company": company,
            "role": role,
            "location": location,
            "duration": duration,
            "link": link,
            "match_score": match_score,
            "status": "Not Applied",
            "date_found": date_found,
            "date_updated": date_found
        }
        
        result = supabase.table('jobs').insert(job_data).execute()
        return True
    except Exception as e:
        # Check if it's a duplicate link error
        if "duplicate" in str(e).lower() or "unique" in str(e).lower():
            return False
        print(f"Error adding job: {e}")
        return False

def get_all_jobs() -> pd.DataFrame:
    """Get all jobs from the database as a DataFrame"""
    if not supabase:
        print("Error: Supabase client not initialized")
        return pd.DataFrame()
    
    try:
        result = supabase.table('jobs').select("*").order('date_found', desc=True).order('match_score', desc=True).execute()
        
        if result.data:
            df = pd.DataFrame(result.data)
            return df
        return pd.DataFrame()
    except Exception as e:
        print(f"Error getting jobs: {e}")
        return pd.DataFrame()

def get_jobs_by_status(status: str) -> pd.DataFrame:
    """Get jobs filtered by status"""
    if not supabase:
        print("Error: Supabase client not initialized")
        return pd.DataFrame()
    
    try:
        result = supabase.table('jobs').select("*").eq('status', status).order('date_found', desc=True).execute()
        
        if result.data:
            return pd.DataFrame(result.data)
        return pd.DataFrame()
    except Exception as e:
        print(f"Error getting jobs by status: {e}")
        return pd.DataFrame()

def update_job_status(job_id: int, new_status: str) -> bool:
    """Update the status of a job"""
    if new_status not in VALID_STATUSES:
        return False
    
    if not supabase:
        print("Error: Supabase client not initialized")
        return False
    
    try:
        date_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        update_data = {
            "status": new_status,
            "date_updated": date_updated
        }
        
        # If status is "Applied", also set date_applied
        if new_status == "Applied":
            update_data["date_applied"] = datetime.now().strftime("%Y-%m-%d")
        
        result = supabase.table('jobs').update(update_data).eq('id', job_id).execute()
        return True
    except Exception as e:
        print(f"Error updating status: {e}")
        return False

def update_job_notes(job_id: int, notes: str) -> bool:
    """Update notes for a job"""
    if not supabase:
        print("Error: Supabase client not initialized")
        return False
    
    try:
        date_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        update_data = {
            "notes": notes,
            "date_updated": date_updated
        }
        
        result = supabase.table('jobs').update(update_data).eq('id', job_id).execute()
        return True
    except Exception as e:
        print(f"Error updating notes: {e}")
        return False

def delete_job(job_id: int) -> bool:
    """Delete a job from the database"""
    if not supabase:
        print("Error: Supabase client not initialized")
        return False
    
    try:
        result = supabase.table('jobs').delete().eq('id', job_id).execute()
        return True
    except Exception as e:
        print(f"Error deleting job: {e}")
        return False

def get_statistics() -> Dict:
    """Get statistics about applications"""
    if not supabase:
        print("Error: Supabase client not initialized")
        return {}
    
    try:
        # Get all jobs for statistics
        all_jobs = get_all_jobs()
        
        stats = {}
        
        # Total jobs
        stats['total_jobs'] = len(all_jobs)
        
        # Count by status
        for status in VALID_STATUSES:
            status_key = status.lower().replace(' ', '_')
            stats[status_key] = len(all_jobs[all_jobs['status'] == status]) if len(all_jobs) > 0 else 0
        
        # Average match score
        if len(all_jobs) > 0:
            avg_score = all_jobs['match_score'].mean()
            stats['avg_match_score'] = round(avg_score, 1) if pd.notna(avg_score) else 0
        else:
            stats['avg_match_score'] = 0
        
        # Success rate (Got Selected / Applied)
        applied = stats['applied'] + stats['ongoing'] + stats['interviewing'] + stats['got_selected'] + stats['rejected']
        if applied > 0:
            stats['success_rate'] = round((stats['got_selected'] / applied) * 100, 1)
        else:
            stats['success_rate'] = 0
        
        return stats
    except Exception as e:
        print(f"Error getting statistics: {e}")
        return {}

def sync_from_excel():
    """Import jobs from Excel to database (one-time migration)"""
    if not os.path.exists(EXCEL_FILE):
        print("No Excel file found to sync from")
        return
    
    if not supabase:
        print("Error: Supabase client not initialized")
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
                # Find the job we just added by link
                result = supabase.table('jobs').select("id").eq('link', row['Link']).execute()
                if result.data and len(result.data) > 0:
                    job_id = result.data[0]['id']
                    update_job_status(job_id, row['Status'])
        
        print(f"✅ Synced {len(df)} jobs from Excel to database")
    except Exception as e:
        print(f"Error syncing from Excel: {e}")

def sync_to_excel():
    """Export database to Excel (for compatibility)"""
    try:
        df = get_all_jobs()
        
        if len(df) == 0:
            print("No jobs to sync to Excel")
            return
        
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

# Initialize database connection on import
if SUPABASE_URL and SUPABASE_KEY:
    init_db()
else:
    print("⚠️ Supabase credentials not found in .env file")
    print("Please add SUPABASE_URL and SUPABASE_KEY to your .env file")
