import pandas as pd
import os
from datetime import datetime
from openpyxl import load_workbook
from openpyxl.worksheet.datavalidation import DataValidation

# Define the path for your tracker
TRACKER_FILE = os.path.join("data", "Job_Application_Tracker.xlsx")

def update_excel_tracker(new_jobs_df):
    """
    Appends ONLY emailed jobs to the Master Excel Tracker with Dropdown Status.
    """
    if new_jobs_df.empty:
        return

    print("📊 Updating Master Excel Tracker with emailed jobs...")

    # 1. Prepare the Data Structure
    export_df = pd.DataFrame()
    export_df['Date Found'] = [datetime.now().strftime("%Y-%m-%d")] * len(new_jobs_df)
    export_df['Company'] = new_jobs_df['company']
    export_df['Role'] = new_jobs_df['title']
    
    # Use .get() to avoid errors if AI didn't find these fields
    export_df['Location'] = new_jobs_df.get('work_mode', 'Unknown') 
    export_df['Duration'] = new_jobs_df.get('duration', 'Not Specified')
    
    export_df['Link'] = new_jobs_df['job_url']
    export_df['Match Score'] = new_jobs_df['relevance_score']
    export_df['Status'] = "Not Applied" # Default Status

    # 2. Check if Tracker exists
    if os.path.exists(TRACKER_FILE):
        existing_df = pd.read_excel(TRACKER_FILE)
        
        # Double-check: Don't add if Link is already in Excel
        export_df = export_df[~export_df['Link'].isin(existing_df['Link'])]
        
        if export_df.empty:
            return

        final_df = pd.concat([existing_df, export_df], ignore_index=True)
    else:
        final_df = export_df

    # 3. Save to Excel
    final_df.to_excel(TRACKER_FILE, index=False)

    # 4. Add Dropdown Menus
    add_dropdowns(TRACKER_FILE, len(final_df))
    print(f"   📝 Added {len(export_df)} jobs to {TRACKER_FILE}")

def add_dropdowns(filename, total_rows):
    """Adds the 'Status' dropdown to the Excel file."""
    try:
        wb = load_workbook(filename)
        ws = wb.active

        # The Dropdown Options
        options = '"Not Applied,Applied,Ongoing,Interviewing,Got Selected,Rejected"'
        dv = DataValidation(type="list", formula1=options, allow_blank=True)
        
        # Apply to Column H (Status), from row 2 down to the end
        dv.add(f'H2:H{total_rows + 50}') 
        
        ws.add_data_validation(dv)
        wb.save(filename)
    except Exception as e:
        print(f"   ⚠️ Could not add dropdowns (System limitation): {e}")