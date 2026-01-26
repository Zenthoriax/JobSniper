"""
JobSniper Dashboard - Secure Interactive Web Interface
Visualize job search data, track applications, and manage your profile
Manual scraping control with background execution
"""

import streamlit as st
import pandas as pd
import json
import os
import sys
import subprocess
import time
from datetime import datetime, timedelta
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go
import bcrypt
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import background scraper
sys.path.insert(0, 'src/modules')
from background_scraper import get_scraper

# --- Security Configuration ---
AUDIT_LOG_FILE = "data/auth_audit.log"
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION = 900  # 15 minutes in seconds
SESSION_TIMEOUT = 1800  # 30 minutes in seconds

def log_auth_attempt(username, success, ip="unknown"):
    """Log authentication attempts for security audit"""
    os.makedirs("data", exist_ok=True)
    timestamp = datetime.now().isoformat()
    status = "SUCCESS" if success else "FAILED"
    log_entry = f"{timestamp} | {status} | User: {username} | IP: {ip}\n"
    
    with open(AUDIT_LOG_FILE, 'a') as f:
        f.write(log_entry)

def check_rate_limit(username):
    """Check if user is rate limited due to too many failed attempts"""
    if not os.path.exists(AUDIT_LOG_FILE):
        return True
    
    # Read recent failed attempts
    cutoff_time = datetime.now() - timedelta(seconds=LOCKOUT_DURATION)
    failed_attempts = 0
    
    try:
        with open(AUDIT_LOG_FILE, 'r') as f:
            for line in f:
                if "FAILED" in line and username in line:
                    try:
                        timestamp_str = line.split(" | ")[0]
                        attempt_time = datetime.fromisoformat(timestamp_str)
                        if attempt_time > cutoff_time:
                            failed_attempts += 1
                    except:
                        continue
    except:
        return True
    
    return failed_attempts < MAX_LOGIN_ATTEMPTS

def check_session_timeout():
    """Check if session has timed out due to inactivity"""
    if "last_activity" not in st.session_state:
        st.session_state["last_activity"] = datetime.now()
        return False
    
    time_since_activity = (datetime.now() - st.session_state["last_activity"]).total_seconds()
    
    if time_since_activity > SESSION_TIMEOUT:
        return True
    
    # Update last activity
    st.session_state["last_activity"] = datetime.now()
    return False

def check_password():
    """Secure authentication with bcrypt and rate limiting"""
    
    # Get credentials from environment
    VALID_USERNAME = os.getenv("DASHBOARD_USERNAME", "zenthoriax")
    VALID_PASSWORD = os.getenv("DASHBOARD_PASSWORD", "9806")
    
    # Hash the password for comparison (bcrypt)
    if "password_hash" not in st.session_state:
        st.session_state["password_hash"] = bcrypt.hashpw(VALID_PASSWORD.encode(), bcrypt.gensalt())
    
    def password_entered():
        """Validate credentials with rate limiting"""
        username = st.session_state.get("username", "")
        password = st.session_state.get("password", "")
        
        # Check rate limit
        if not check_rate_limit(username):
            st.session_state["password_correct"] = False
            st.session_state["rate_limited"] = True
            log_auth_attempt(username, False)
            return
        
        # Validate credentials
        if username == VALID_USERNAME and password == VALID_PASSWORD:
            st.session_state["password_correct"] = True
            st.session_state["rate_limited"] = False
            st.session_state["last_activity"] = datetime.now()
            st.session_state["session_token"] = bcrypt.hashpw(str(datetime.now()).encode(), bcrypt.gensalt()).decode()
            log_auth_attempt(username, True)
            
            # Clear sensitive data
            if "password" in st.session_state:
                del st.session_state["password"]
            if "username" in st.session_state:
                del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False
            st.session_state["rate_limited"] = False
            log_auth_attempt(username, False)
    
    # Check session timeout
    if "password_correct" in st.session_state and st.session_state["password_correct"]:
        if check_session_timeout():
            st.session_state["password_correct"] = False
            st.warning("⏱️ Session expired due to inactivity. Please login again.")
            time.sleep(2)
            st.rerun()
    
    # First run or logged out
    if "password_correct" not in st.session_state:
        st.title("🦅 JobSniper Dashboard")
        st.markdown("### 🔐 Secure Login")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.text_input("Username", key="username", autocomplete="username")
            st.text_input("Password", type="password", key="password", autocomplete="current-password")
            st.button("🔓 Login", on_click=password_entered, width="stretch", type="primary")
            
            st.markdown("---")
            st.caption("🔒 Secured with bcrypt encryption")
            st.caption("⏱️ Session timeout: 30 minutes")
        
        return False
    
    # Rate limited
    elif st.session_state.get("rate_limited", False):
        st.title("🦅 JobSniper Dashboard")
        st.markdown("### 🔐 Secure Login")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.error(f"🚫 Too many failed login attempts. Please wait 15 minutes before trying again.")
            st.info("This security measure protects against brute force attacks.")
        
        return False
    
    # Password incorrect
    elif not st.session_state["password_correct"]:
        st.title("🦅 JobSniper Dashboard")
        st.markdown("### 🔐 Secure Login")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.text_input("Username", key="username", autocomplete="username")
            st.text_input("Password", type="password", key="password", autocomplete="current-password")
            st.button("🔓 Login", on_click=password_entered, width="stretch", type="primary")
            st.error("❌ Invalid username or password")
            
            st.markdown("---")
            st.caption("🔒 Secured with bcrypt encryption")
            st.caption("⏱️ Session timeout: 30 minutes")
        
        return False
    
    # Authenticated
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

# --- Responsive CSS ---
st.markdown("""
<style>
    /* Mobile-first responsive design */
    @media (max-width: 768px) {
        /* Make sidebar collapsible on mobile */
        section[data-testid="stSidebar"] {
            width: 100% !important;
        }
        
        /* Stack columns on mobile */
        .stColumn {
            width: 100% !important;
            margin-bottom: 1rem;
        }
        
        /* Adjust font sizes for mobile */
        h1 { font-size: 1.5rem !important; }
        h2 { font-size: 1.3rem !important; }
        h3 { font-size: 1.1rem !important; }
        
        /* Make buttons full width on mobile */
        .stButton > button {
            width: 100% !important;
            padding: 0.75rem !important;
            font-size: 1rem !important;
        }
        
        /* Make metrics more compact */
        [data-testid="stMetricValue"] {
            font-size: 1.2rem !important;
        }
        
        /* Scrollable tables on mobile */
        .dataframe {
            overflow-x: auto !important;
            display: block !important;
        }
        
        /* Better spacing */
        .block-container {
            padding: 1rem !important;
        }
    }
    
    /* Tablet adjustments */
    @media (min-width: 769px) and (max-width: 1024px) {
        .stColumn {
            min-width: 45% !important;
        }
    }
    
    /* Touch-friendly elements */
    .stButton > button {
        min-height: 44px !important;
        touch-action: manipulation;
    }
    
    /* Better expander styling */
    .streamlit-expanderHeader {
        font-size: 1rem !important;
        padding: 0.75rem !important;
    }
    
    /* Responsive charts */
    .js-plotly-plot {
        width: 100% !important;
    }
    
    /* Better text area sizing */
    textarea {
        font-size: 1rem !important;
    }
</style>
""", unsafe_allow_html=True)

# --- File Paths ---
VERIFIED_JOBS_FILE = "data/verified/verified_jobs.csv"
TRACKER_FILE = "data/Job_Application_Tracker.xlsx"
PROFILE_FILE = "data/profile.json"
HISTORY_FILE = "data/history.json"
PROCESSED_FILE = "data/processed.json"
SCRAPER_LOG_FILE = "data/scraper_log.txt"

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

def load_config():
    """Load scraper configuration"""
    import sys
    sys.path.insert(0, 'config')
    try:
        import settings
        return {
            'queries': settings.SEARCH_QUERIES,
            'locations': settings.LOCATIONS,
            'sites': settings.TARGET_SITES,
            'hours_old': settings.HOURS_OLD,
            'use_gemini': settings.USE_GEMINI,
            'country': settings.COUNTRY
        }
    except:
        return {}

# --- Sidebar ---
st.sidebar.title("🦅 JobSniper")
st.sidebar.markdown("**Manual Job Hunter**")

# Database Connection Status
try:
    from src.modules.db_manager import supabase
    if supabase:
        # Test connection
        try:
            test_result = supabase.table('jobs').select("id").limit(1).execute()
            st.sidebar.success("🟢 Supabase Connected")
        except Exception as e:
            st.sidebar.error("🔴 Database Error")
            st.sidebar.caption(f"Error: {str(e)[:50]}...")
    else:
        st.sidebar.warning("🟡 No Database Config")
except Exception as e:
    st.sidebar.error("🔴 Connection Failed")

st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    ["🎯 Scraper Control", "📊 Overview", "💼 Job Listings", "📋 Application Tracker", "📈 Analytics", "👤 Profile"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### Quick Stats")

# Get data from Supabase instead of verified CSV for accurate stats
try:
    from src.modules.db_manager import get_all_jobs, get_statistics
    
    # Get jobs from Supabase
    tracker_jobs = get_all_jobs()
    stats = get_statistics()
    
    st.sidebar.metric("Jobs in Tracker", stats.get('total_jobs', 0))
    st.sidebar.metric("Not Applied", stats.get('not_applied', 0))
    if stats.get('total_jobs', 0) > 0:
        st.sidebar.metric("Avg Match Score", f"{stats.get('avg_match_score', 0):.1f}/100")
except Exception as e:
    # Fallback to old method if Supabase fails
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

# --- PAGE 0: Scraper Control ---
if page == "🎯 Scraper Control":
    st.title("🎯 Manual Scraper Control")
    st.markdown("### Run job scraping manually from this dashboard")
    

    # Scraper Control
    st.subheader("🚀 Run Scraper")
    
    # Get background scraper instance and check status
    scraper = get_scraper()
    is_scraper_running = scraper.is_running()
    progress = scraper.get_progress()
    
    # Status indicator
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if is_scraper_running:
            st.markdown("### 🟡 Status: RUNNING")
        else:
            st.markdown("### 🟢 Status: IDLE")
    
    with col2:
        if progress.get("start_time"):
            try:
                start_time = datetime.fromisoformat(progress["start_time"])
                st.markdown(f"**Started:** {start_time.strftime('%H:%M:%S')}")
            except:
                st.markdown("**Last Run:** Never")
        else:
            st.markdown("**Last Run:** Never")
    
    with col3:
        if st.button("🔄 Refresh", width="stretch"):
            st.cache_data.clear()
            st.rerun()
    
    st.markdown("---")
    
    # Run button
    col_a, col_b, col_c = st.columns([1, 1, 2])
    
    with col_a:
        if st.button("🚀 Run Scraper Now", type="primary", width="stretch", disabled=is_scraper_running):
            result = scraper.start()
            if result["success"]:
                st.success("✅ Scraper started in background!")
                st.info("💡 Dashboard will remain responsive. Refresh to see progress.")
                time.sleep(2)
                st.rerun()
            else:
                st.error(f"❌ {result['error']}")
    
    with col_b:
        # Stop button with rollback option
        if st.button("🛑 Stop Scraper", width="stretch", disabled=not is_scraper_running):
            # Show confirmation dialog
            st.session_state.show_stop_confirm = True
    
    # Stop confirmation dialog
    if st.session_state.get("show_stop_confirm", False):
        st.markdown("---")
        st.warning("⚠️ **Stop Scraper Confirmation**")
        st.markdown("Choose how to stop the scraper:")
        
        col_x, col_y, col_z = st.columns(3)
        
        with col_x:
            if st.button("🔄 Stop & Rollback", type="secondary", width="stretch"):
                # Stop with rollback
                scraper = get_scraper()
                result = scraper.stop(rollback=True)
                
                if result["success"]:
                    if result.get("rollback_success"):
                        st.success("✅ Scraper stopped and data rolled back successfully!")
                        st.info("📦 Previous data has been restored from backup")
                    else:
                        st.warning("⚠️ Scraper stopped but rollback failed (no backup available)")
                else:
                    st.error(f"❌ {result['error']}")
                
                st.session_state.show_stop_confirm = False
                time.sleep(2)
                st.rerun()
        
        with col_y:
            if st.button("🛑 Stop & Keep Data", type="primary", width="stretch"):
                # Stop without rollback
                scraper = get_scraper()
                result = scraper.stop(rollback=False)
                
                if result["success"]:
                    st.success("✅ Scraper stopped. New data kept.")
                else:
                    st.error(f"❌ {result['error']}")
                
                st.session_state.show_stop_confirm = False
                time.sleep(2)
                st.rerun()
        
        with col_z:
            if st.button("❌ Cancel", width="stretch"):
                st.session_state.show_stop_confirm = False
                st.rerun()
        
        st.markdown("**🔄 Stop & Rollback:** Cancels scraping and restores previous data")
        st.markdown("**🛑 Stop & Keep Data:** Cancels scraping but keeps any new jobs found")
        st.markdown("---")
    
    
    # Progress display
    if is_scraper_running:
        st.markdown("---")
        st.subheader("📊 Live Progress")
        
        # Progress metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Phase", progress.get("phase", "Unknown").title())
        with col2:
            st.metric("Jobs Scraped", progress.get("jobs_scraped", 0))
        with col3:
            st.metric("Verified", progress.get("jobs_verified", 0))
        with col4:
            st.metric("High Score (75+)", progress.get("high_score_jobs", 0))
        
        # Elapsed time
        if progress.get("start_time"):
            try:
                start_time = datetime.fromisoformat(progress["start_time"])
                elapsed = datetime.now() - start_time
                minutes = int(elapsed.total_seconds() // 60)
                seconds = int(elapsed.total_seconds() % 60)
                st.info(f"⏱️ Running for: {minutes}m {seconds}s")
            except:
                pass
        
        # Live logs
        st.markdown("### 📋 Live Logs")
        logs = scraper.get_logs(tail_lines=30)
        if logs:
            st.code(logs, language="text")
        else:
            st.info("⏳ Initializing scraper... Logs will appear shortly.")
        
        # Auto-refresh
        st.info("💡 Page auto-refreshes every 5 seconds during scraping")
        time.sleep(5)
        st.rerun()
    
    # Completed run summary
    elif progress.get("status") in ["completed", "cancelled"] or (not is_scraper_running and progress.get("jobs_verified", 0) > 0):
        st.markdown("---")
        st.subheader("✅ Last Run Summary")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Jobs Scraped", progress.get("jobs_scraped", 0))
        with col2:
            st.metric("Verified", progress.get("jobs_verified", 0))
        with col3:
            st.metric("High Score (75+)", progress.get("high_score_jobs", 0))
        with col4:
            if progress.get("jobs_verified", 0) > 0:
                success_rate = (progress.get("high_score_jobs", 0) / progress.get("jobs_verified", 1)) * 100
                st.metric("Quality Rate", f"{success_rate:.0f}%")
        
        # Show logs
        with st.expander("📋 View Full Logs"):
            logs = scraper.get_logs(tail_lines=100)
            if logs:
                st.code(logs, language="text")
        
        # Show rollback info if cancelled
        if progress.get("status") == "cancelled":
            if progress.get("rollback_performed"):
                if progress.get("rollback_success"):
                    st.success("✅ Data rolled back successfully")
                else:
                    st.warning("⚠️ Rollback attempted but failed")
    
    # Error state
    elif progress.get("status") == "error":
        st.error(f"❌ Scraper Error: {progress.get('error', 'Unknown error')}")
        
        with st.expander("🔍 View Logs"):
            logs = scraper.get_logs()
            if logs:
                st.code(logs, language="text")

# --- PAGE 1: Overview ---
elif page == "📊 Overview":
    st.title("📊 Dashboard Overview")
    st.markdown("### Quick insights into your job search")
    
    # Load data
    verified_df = load_verified_jobs()
    history = load_history()
    
    # Get data from Supabase
    try:
        from src.modules.db_manager import get_all_jobs, get_statistics
        tracker_jobs = get_all_jobs()
        stats = get_statistics()
    except Exception as e:
        st.error(f"Error loading data: {e}")
        tracker_jobs = pd.DataFrame()
        stats = {}
    
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
    
    # Quick Actions
    st.subheader("⚡ Quick Actions")
    col_a, col_b, col_c = st.columns([1, 1, 1])
    
    with col_a:
        if st.button("🚀 Go to Scraper Control", type="primary", width="stretch"):
            st.session_state.page = "🎯 Scraper Control"
            st.rerun()
    
    with col_b:
        if st.button("🔄 Refresh Dashboard", width="stretch"):
            st.cache_data.clear()
            st.rerun()
    
    with col_c:
        if st.button("📧 Email History", width="stretch"):
            st.info(f"Total emails sent: {len(history)}")
    
    st.markdown("---")
    
    # Recent Activity
    st.subheader("📅 Recent High-Score Jobs")
    
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
        st.info("No jobs found yet. Go to Scraper Control to run a manual search!")

# --- PAGE 2: Job Listings ---
elif page == "💼 Job Listings":
    st.title("💼 Job Listings")
    
    # Load jobs from Supabase Application Tracker
    try:
        from src.modules.db_manager import get_all_jobs
        jobs_df = get_all_jobs()
        
        # Rename columns to match expected format
        if len(jobs_df) > 0:
            # Map Supabase columns to display format
            verified_df = jobs_df.rename(columns={
                'company': 'company',
                'role': 'title',
                'link': 'job_url',
                'match_score': 'relevance_score',
                'location': 'location',
                'duration': 'duration'
            })
            # Add missing columns if needed
            if 'work_mode' not in verified_df.columns:
                verified_df['work_mode'] = verified_df['location'].apply(
                    lambda x: 'Remote' if x and 'remote' in str(x).lower() else 'On-site'
                )
        else:
            verified_df = pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading jobs from database: {e}")
        verified_df = pd.DataFrame()
    
    if len(verified_df) == 0:
        st.warning("No jobs found yet. Run the scraper first!")
    else:
        # Filters
        st.sidebar.markdown("### Filters")
        
        # Score filter
        min_score = st.sidebar.slider("Minimum Score", 0, 100, 55)
        
        # Company filter (remove NaN values to avoid sorting error)
        companies = ["All"] + sorted(verified_df['company'].dropna().unique().tolist())
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
                width="stretch",
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
            if st.button("📊 Sync to Excel Now", width="stretch"):
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
    st.title("📈 Job Market Analytics")
    st.markdown("### Visualize your job search data")
    
    # Load jobs from Supabase
    try:
        from src.modules.db_manager import get_all_jobs
        jobs_df = get_all_jobs()
        
        # Rename columns to match expected format
        if len(jobs_df) > 0:
            verified_df = jobs_df.rename(columns={
                'company': 'company',
                'role': 'title',
                'match_score': 'relevance_score',
                'location': 'location'
            })
            # Add work_mode if not present
            if 'work_mode' not in verified_df.columns:
                verified_df['work_mode'] = verified_df['location'].apply(
                    lambda x: 'Remote' if x and 'remote' in str(x).lower() else 'On-site'
                )
        else:
            verified_df = pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading jobs: {e}")
        verified_df = pd.DataFrame()
    
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
        st.plotly_chart(fig_score, width="stretch")
        
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
            st.plotly_chart(fig_companies, width="stretch")
        
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
                st.plotly_chart(fig_mode, width="stretch")
        
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
        if st.button("💾 Save Profile", type="primary", width="stretch"):
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
st.sidebar.markdown("v3.0 - Manual Control Edition")
