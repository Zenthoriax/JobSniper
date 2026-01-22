"""
JobSniper Dashboard - Interactive Web Interface
Visualize job search data, track applications, and manage your profile
"""

import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import hashlib

# --- Authentication Configuration ---
VALID_USERNAME = "zenthoriax"
VALID_PASSWORD_HASH = hashlib.sha256("9806".encode()).hexdigest()

def check_password():
    """Returns `True` if the user had the correct password."""
    
    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if (st.session_state["username"] == VALID_USERNAME and 
            hashlib.sha256(st.session_state["password"].encode()).hexdigest() == VALID_PASSWORD_HASH):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store password
            del st.session_state["username"]  # Don't store username
        else:
            st.session_state["password_correct"] = False

    # First run, show login screen
    if "password_correct" not in st.session_state:
        st.title("🦅 JobSniper Dashboard")
        st.markdown("### 🔐 Login Required")
        st.text_input("Username", key="username")
        st.text_input("Password", type="password", key="password")
        st.button("Login", on_click=password_entered)
        return False
    
    # Password incorrect, show error and login again
    elif not st.session_state["password_correct"]:
        st.title("🦅 JobSniper Dashboard")
        st.markdown("### 🔐 Login Required")
        st.text_input("Username", key="username")
        st.text_input("Password", type="password", key="password")
        st.button("Login", on_click=password_entered)
        st.error("😕 Username or password incorrect")
        return False
    
    # Password correct
    else:
        return True

# Check authentication before showing dashboard
if not check_password():
    st.stop()

# --- Configuration ---
st.set_page_config(
    page_title="JobSniper Dashboard",
    page_icon="🦅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- File Paths ---
VERIFIED_JOBS_FILE = "data/verified/verified_jobs.csv"
TRACKER_FILE = "data/Job_Application_Tracker.xlsx"
PROFILE_FILE = "data/profile.json"
HISTORY_FILE = "data/history.json"
PROCESSED_FILE = "data/processed.json"

# --- Helper Functions ---
@st.cache_data(ttl=60)
def load_verified_jobs():
    """Load verified jobs from CSV"""
    if os.path.exists(VERIFIED_JOBS_FILE):
        df = pd.read_csv(VERIFIED_JOBS_FILE)
        df['relevance_score'] = pd.to_numeric(df['relevance_score'], errors='coerce').fillna(0)
        return df
    return pd.DataFrame()

@st.cache_data(ttl=60)
def load_tracker():
    """Load application tracker from Excel"""
    if os.path.exists(TRACKER_FILE):
        return pd.read_excel(TRACKER_FILE)
    return pd.DataFrame()

def load_profile():
    """Load user profile"""
    if os.path.exists(PROFILE_FILE):
        with open(PROFILE_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_profile(profile_data):
    """Save user profile"""
    with open(PROFILE_FILE, 'w') as f:
        json.dump(profile_data, f, indent=2)

def load_history():
    """Load email history"""
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            return json.load(f)
    return []

def load_processed():
    """Load processed jobs"""
    if os.path.exists(PROCESSED_FILE):
        with open(PROCESSED_FILE, 'r') as f:
            return json.load(f)
    return []

# --- Sidebar ---
st.sidebar.title("🦅 JobSniper")
st.sidebar.markdown("**Autonomous Job Hunter**")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    ["📊 Overview", "💼 Job Listings", "📋 Application Tracker", "📈 Analytics", "👤 Profile"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Quick Stats")
verified_df = load_verified_jobs()
history = load_history()
st.sidebar.metric("Total Jobs Found", len(verified_df))
st.sidebar.metric("Jobs Emailed", len(history))
if len(verified_df) > 0:
    st.sidebar.metric("Avg Match Score", f"{verified_df['relevance_score'].mean():.1f}/100")

# Logout button
st.sidebar.markdown("---")
if st.sidebar.button("🚪 Logout"):
    st.session_state["password_correct"] = False
    st.rerun()

# --- PAGE 1: Overview ---
if page == "📊 Overview":
    st.title("🦅 JobSniper Dashboard")
    st.markdown("### Welcome to your autonomous job hunting command center!")
    
    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="📧 Jobs Emailed",
            value=len(history),
            delta=f"{len(verified_df) - len(history)} pending"
        )
    
    with col2:
        if len(verified_df) > 0:
            high_score_jobs = len(verified_df[verified_df['relevance_score'] >= 75])
            st.metric(
                label="⭐ High Score Jobs",
                value=high_score_jobs,
                delta=f"{(high_score_jobs/len(verified_df)*100):.0f}%"
            )
        else:
            st.metric(label="⭐ High Score Jobs", value=0)
    
    with col3:
        tracker_df = load_tracker()
        if len(tracker_df) > 0:
            applied = len(tracker_df[tracker_df['Status'] == 'Applied'])
            st.metric(label="✅ Applications Sent", value=applied)
        else:
            st.metric(label="✅ Applications Sent", value=0)
    
    with col4:
        processed = load_processed()
        st.metric(label="🔍 Total Jobs Scanned", value=len(processed))
    
    st.markdown("---")
    
    # Recent Activity
    st.subheader("📅 Recent Activity")
    
    if len(verified_df) > 0:
        recent_jobs = verified_df.sort_values('relevance_score', ascending=False).head(5)
        
        for idx, job in recent_jobs.iterrows():
            with st.container():
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.markdown(f"**{job['title']}** at *{job['company']}*")
                
                with col2:
                    score = job['relevance_score']
                    color = "🟢" if score >= 75 else "🟡" if score >= 60 else "🔴"
                    st.markdown(f"{color} **{score:.0f}/100**")
                
                with col3:
                    st.markdown(f"[Apply]({job['job_url']})")
                
                st.markdown("---")
    else:
        st.info("No jobs found yet. Run the scraper to get started!")
    
    # Quick Actions
    st.subheader("⚡ Quick Actions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Refresh Data", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    
    with col2:
        if st.button("📧 View Email History", use_container_width=True):
            st.info(f"Total emails sent: {len(history)}")
    
    with col3:
        if st.button("📊 View Full Analytics", use_container_width=True):
            st.switch_page

# --- PAGE 2: Job Listings ---
elif page == "💼 Job Listings":
    st.title("💼 Job Listings")
    
    if len(verified_df) == 0:
        st.warning("No jobs found yet. Run the scraper first!")
    else:
        # Filters
        st.sidebar.markdown("### Filters")
        
        # Score filter
        min_score = st.sidebar.slider("Minimum Score", 0, 100, 55)
        
        # Company filter
        companies = ["All"] + sorted(verified_df['company'].unique().tolist())
        selected_company = st.sidebar.selectbox("Company", companies)
        
        # Work mode filter
        if 'work_mode' in verified_df.columns:
            work_modes = ["All"] + sorted(verified_df['work_mode'].dropna().unique().tolist())
            selected_mode = st.sidebar.selectbox("Work Mode", work_modes)
        else:
            selected_mode = "All"
        
        # Apply filters
        filtered_df = verified_df[verified_df['relevance_score'] >= min_score]
        
        if selected_company != "All":
            filtered_df = filtered_df[filtered_df['company'] == selected_company]
        
        if selected_mode != "All" and 'work_mode' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['work_mode'] == selected_mode]
        
        # Sort options
        sort_by = st.selectbox("Sort by", ["Score (High to Low)", "Score (Low to High)", "Company (A-Z)"])
        
        if sort_by == "Score (High to Low)":
            filtered_df = filtered_df.sort_values('relevance_score', ascending=False)
        elif sort_by == "Score (Low to High)":
            filtered_df = filtered_df.sort_values('relevance_score', ascending=True)
        else:
            filtered_df = filtered_df.sort_values('company')
        
        st.markdown(f"### Showing {len(filtered_df)} jobs")
        
        # Display jobs
        for idx, job in filtered_df.iterrows():
            with st.expander(f"**{job['title']}** at {job['company']} - Score: {job['relevance_score']:.0f}/100"):
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.markdown(f"**Company:** {job['company']}")
                    st.markdown(f"**Role:** {job['title']}")
                    
                    if 'work_mode' in job and pd.notna(job['work_mode']):
                        st.markdown(f"**Work Mode:** {job['work_mode']}")
                    
                    if 'duration' in job and pd.notna(job['duration']):
                        st.markdown(f"**Duration:** {job['duration']}")
                    
                    if 'match_reason' in job and pd.notna(job['match_reason']):
                        st.markdown(f"**Why this matches:**")
                        st.info(job['match_reason'])
                
                with col2:
                    score = job['relevance_score']
                    if score >= 75:
                        st.success(f"⭐ Excellent Match\n\n**{score:.0f}/100**")
                    elif score >= 60:
                        st.warning(f"✅ Good Match\n\n**{score:.0f}/100**")
                    else:
                        st.info(f"📌 Potential Match\n\n**{score:.0f}/100**")
                    
                    st.markdown(f"[🚀 Apply Now]({job['job_url']})")

# --- PAGE 3: Application Tracker ---
elif page == "📋 Application Tracker":
    st.title("📋 Application Tracker")
    
    # Import database manager
    import sys
    sys.path.insert(0, 'src/modules')
    from db_manager import (
        get_all_jobs, get_jobs_by_status, update_job_status, 
        update_job_notes, delete_job, get_statistics, sync_to_excel,
        VALID_STATUSES
    )
    
    # Get statistics
    stats = get_statistics()
    
    # Summary stats
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Total Jobs", stats['total_jobs'])
    with col2:
        st.metric("Not Applied", stats['not_applied'])
    with col3:
        st.metric("Applied", stats['applied'])
    with col4:
        st.metric("Interviewing", stats['interviewing'])
    with col5:
        st.metric("Got Selected", stats['got_selected'], delta=f"{stats['success_rate']}% success")
    
    st.markdown("---")
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["📋 All Applications", "📊 By Status", "➕ Quick Actions"])
    
    with tab1:
        st.subheader("All Applications")
        
        # Get all jobs
        jobs_df = get_all_jobs()
        
        if len(jobs_df) == 0:
            st.info("No applications tracked yet. Jobs will appear here after the scraper runs and emails you.")
        else:
            # Display each job as an interactive card
            for idx, job in jobs_df.iterrows():
                with st.expander(f"**{job['company']}** - {job['role']} ({job['status']})", expanded=False):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.markdown(f"**Company:** {job['company']}")
                        st.markdown(f"**Role:** {job['role']}")
                        st.markdown(f"**Location:** {job['location'] if pd.notna(job['location']) else 'N/A'}")
                        st.markdown(f"**Duration:** {job['duration'] if pd.notna(job['duration']) else 'N/A'}")
                        st.markdown(f"**Match Score:** {job['match_score']:.0f}/100")
                        st.markdown(f"**Date Found:** {job['date_found']}")
                        if pd.notna(job['date_applied']):
                            st.markdown(f"**Date Applied:** {job['date_applied']}")
                        
                        st.markdown(f"[🔗 View Job]({job['link']})")
                    
                    with col2:
                        # Status badge
                        status_colors = {
                            "Not Applied": "🔵",
                            "Applied": "🟡",
                            "Ongoing": "🟠",
                            "Interviewing": "🟣",
                            "Got Selected": "🟢",
                            "Rejected": "🔴"
                        }
                        st.markdown(f"### {status_colors.get(job['status'], '⚪')} {job['status']}")
                        
                        # Update status
                        new_status = st.selectbox(
                            "Change Status",
                            VALID_STATUSES,
                            index=VALID_STATUSES.index(job['status']),
                            key=f"status_{job['id']}"
                        )
                        
                        if st.button("💾 Update Status", key=f"update_{job['id']}"):
                            if update_job_status(job['id'], new_status):
                                sync_to_excel()
                                st.success("Status updated!")
                                st.cache_data.clear()
                                st.rerun()
                    
                    # Notes section
                    st.markdown("---")
                    st.markdown("**📝 Notes:**")
                    current_notes = job['notes'] if pd.notna(job['notes']) else ""
                    notes = st.text_area(
                        "Add notes/comments",
                        value=current_notes,
                        key=f"notes_{job['id']}",
                        height=100
                    )
                    
                    col_a, col_b = st.columns([1, 1])
                    with col_a:
                        if st.button("💾 Save Notes", key=f"save_notes_{job['id']}"):
                            if update_job_notes(job['id'], notes):
                                sync_to_excel()
                                st.success("Notes saved!")
                                st.cache_data.clear()
                    
                    with col_b:
                        if st.button("🗑️ Delete Job", key=f"delete_{job['id']}", type="secondary"):
                            if delete_job(job['id']):
                                sync_to_excel()
                                st.success("Job deleted!")
                                st.cache_data.clear()
                                st.rerun()
    
    with tab2:
        st.subheader("Filter by Status")
        
        selected_status = st.selectbox("Select Status", VALID_STATUSES)
        filtered_jobs = get_jobs_by_status(selected_status)
        
        if len(filtered_jobs) == 0:
            st.info(f"No jobs with status '{selected_status}'")
        else:
            st.markdown(f"**{len(filtered_jobs)} jobs found**")
            
            # Display as simple table
            display_df = filtered_jobs[['company', 'role', 'location', 'match_score', 'date_found', 'link']]
            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "link": st.column_config.LinkColumn("Apply Link"),
                    "match_score": st.column_config.ProgressColumn(
                        "Match Score",
                        min_value=0,
                        max_value=100,
                    )
                }
            )
    
    with tab3:
        st.subheader("Quick Actions")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🔄 Sync to Excel")
            st.markdown("Export all database entries to Excel file")
            if st.button("📊 Sync to Excel Now", use_container_width=True):
                sync_to_excel()
                st.success("✅ Synced to Excel successfully!")
        
        with col2:
            st.markdown("### 📈 Statistics")
            st.markdown(f"**Total Jobs:** {stats['total_jobs']}")
            st.markdown(f"**Applied:** {stats['applied']}")
            st.markdown(f"**Success Rate:** {stats['success_rate']}%")
            st.markdown(f"**Avg Match Score:** {stats['avg_match_score']}/100")

# --- PAGE 4: Analytics ---
elif page == "📈 Analytics":
    st.title("📈 Analytics & Insights")
    
    if len(verified_df) == 0:
        st.warning("No data available yet. Run the scraper first!")
    else:
        # Score Distribution
        st.subheader("📊 Score Distribution")
        fig_score = px.histogram(
            verified_df,
            x='relevance_score',
            nbins=20,
            title="Job Match Score Distribution",
            labels={'relevance_score': 'Match Score', 'count': 'Number of Jobs'},
            color_discrete_sequence=['#1f77b4']
        )
        st.plotly_chart(fig_score, use_container_width=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Top Companies
            st.subheader("🏢 Top Companies Hiring")
            company_counts = verified_df['company'].value_counts().head(10)
            fig_companies = px.bar(
                x=company_counts.values,
                y=company_counts.index,
                orientation='h',
                title="Top 10 Companies",
                labels={'x': 'Number of Jobs', 'y': 'Company'},
                color_discrete_sequence=['#2ecc71']
            )
            fig_companies.update_layout(showlegend=False)
            st.plotly_chart(fig_companies, use_container_width=True)
        
        with col2:
            # Work Mode Distribution
            if 'work_mode' in verified_df.columns:
                st.subheader("🌍 Work Mode Distribution")
                work_mode_counts = verified_df['work_mode'].value_counts()
                fig_mode = px.pie(
                    values=work_mode_counts.values,
                    names=work_mode_counts.index,
                    title="Remote vs On-site vs Hybrid",
                    color_discrete_sequence=px.colors.qualitative.Set3
                )
                st.plotly_chart(fig_mode, use_container_width=True)
        
        # Key Insights
        st.subheader("💡 Key Insights")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            avg_score = verified_df['relevance_score'].mean()
            st.metric("Average Match Score", f"{avg_score:.1f}/100")
        
        with col2:
            top_company = verified_df['company'].value_counts().index[0]
            top_count = verified_df['company'].value_counts().values[0]
            st.metric("Most Active Company", top_company, f"{top_count} jobs")
        
        with col3:
            high_score = len(verified_df[verified_df['relevance_score'] >= 75])
            st.metric("Excellent Matches (75+)", high_score, f"{(high_score/len(verified_df)*100):.0f}%")

# --- PAGE 5: Profile Management ---
elif page == "👤 Profile":
    st.title("👤 Profile Management")
    
    profile = load_profile()
    
    if not profile:
        st.warning("Profile not found. Please create data/profile.json first.")
    else:
        st.subheader("📝 Your Profile")
        
        # Basic Info
        with st.expander("👤 Basic Information", expanded=True):
            name = st.text_input("Name", value=profile.get('name', ''))
            target_role = st.text_input("Target Role", value=profile.get('target_role', ''))
            
            if 'contact' in profile:
                email = st.text_input("Email", value=profile['contact'].get('email', ''))
                location = st.text_input("Location", value=profile['contact'].get('location', ''))
        
        # Skills
        with st.expander("🛠️ Skills", expanded=True):
            current_skills = profile.get('skills', [])
            skills_text = st.text_area(
                "Skills (one per line)",
                value="\n".join(current_skills),
                height=200
            )
        
        # Preferences
        with st.expander("⚙️ Preferences", expanded=True):
            if 'preferences' in profile:
                prefs = profile['preferences']
                locations = st.text_area(
                    "Preferred Locations (one per line)",
                    value="\n".join(prefs.get('locations', [])),
                    height=100
                )
                work_type = st.text_input("Work Type", value=prefs.get('work_type', ''))
                min_duration = st.text_input("Minimum Duration", value=prefs.get('min_duration', ''))
        
        # Save Button
        if st.button("💾 Save Profile", type="primary", use_container_width=True):
            # Update profile
            profile['name'] = name
            profile['target_role'] = target_role
            
            if 'contact' not in profile:
                profile['contact'] = {}
            profile['contact']['email'] = email
            profile['contact']['location'] = location
            
            profile['skills'] = [s.strip() for s in skills_text.split('\n') if s.strip()]
            
            if 'preferences' not in profile:
                profile['preferences'] = {}
            profile['preferences']['locations'] = [l.strip() for l in locations.split('\n') if l.strip()]
            profile['preferences']['work_type'] = work_type
            profile['preferences']['min_duration'] = min_duration
            
            save_profile(profile)
            st.success("✅ Profile saved successfully!")
            st.cache_data.clear()
        
        # Display current profile
        st.markdown("---")
        st.subheader("📄 Current Profile JSON")
        st.json(profile)

# --- Footer ---
st.sidebar.markdown("---")
st.sidebar.markdown("Made with ❤️ by JobSniper")
st.sidebar.markdown("v2.1 - Dashboard Edition")
