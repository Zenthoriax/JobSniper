"""
Data Migration Page for Streamlit Dashboard
Upload CSV data to Supabase from the deployed app
"""

import streamlit as st
import pandas as pd
import sys
import os

sys.path.insert(0, 'src/modules')
from db_connector import get_db

st.set_page_config(page_title="Data Migration", page_icon="📤")

st.title("📤 Migrate CSV Data to Database")

st.markdown("""
This tool uploads your existing CSV data to the cloud database.
Run this once after deployment to load all your historical jobs.
""")

# Get database connection
db = get_db()

if not db.use_database:
    st.error("❌ Database connection failed")
    st.info("Make sure DATABASE_URL is set in Streamlit Cloud secrets")
    st.stop()

st.success("✅ Connected to database")

# File uploader
st.markdown("### Upload verified_jobs.csv")
uploaded_file = st.file_uploader("Choose your verified_jobs.csv file", type=['csv'])

if uploaded_file is not None:
    # Read CSV
    df = pd.read_csv(uploaded_file)
    st.info(f"📂 Found {len(df)} jobs in CSV")
    
    # Show preview
    with st.expander("📋 Preview data"):
        st.dataframe(df.head(10))
    
    # Migration button
    if st.button("🚀 Upload to Database", type="primary"):
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        migrated = 0
        skipped = 0
        total = len(df)
        
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
            else:
                skipped += 1
            
            # Update progress
            progress = (idx + 1) / total
            progress_bar.progress(progress)
            status_text.text(f"Uploading... {idx + 1}/{total}")
        
        # Show results
        st.success("🎉 Migration Complete!")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("✅ Migrated", migrated)
        with col2:
            st.metric("⏭️ Skipped (duplicates)", skipped)
        
        # Verify
        db_jobs = db.get_verified_jobs()
        st.info(f"📊 Database now has {len(db_jobs)} total jobs")
        
        st.balloons()

# Show current database stats
st.markdown("---")
st.markdown("### 📊 Current Database Stats")

db_jobs = db.get_verified_jobs()
st.metric("Total Jobs in Database", len(db_jobs))

if len(db_jobs) > 0:
    st.markdown("#### Recent Jobs")
    st.dataframe(db_jobs.head(5)[['title', 'company', 'relevance_score', 'work_mode']])
