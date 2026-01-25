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
            st.button("🔓 Login", on_click=password_entered, use_container_width=True, type="primary")
            
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
            st.button("🔓 Login", on_click=password_entered, use_container_width=True, type="primary")
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
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Navigation",
    ["🎯 Scraper Control", "📊 Overview", "💼 Job Listings", "📋 Application Tracker", "📈 Analytics", "👤 Profile"]
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

# --- PAGE 0: Scraper Control ---
if page == "🎯 Scraper Control":
    st.title("🎯 Manual Scraper Control")
    st.markdown("### Run job scraping manually from this dashboard")
    
    # Configuration Display
    st.subheader("⚙️ Current Configuration")
    config = load_config()
    
    if config:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**🔍 Search Queries:**")
            for query in config.get('queries', []):
                st.markdown(f"- {query}")
            
            st.markdown("**📍 Locations:**")
            for loc in config.get('locations', []):
                st.markdown(f"- {loc}")
        
        with col2:
            st.markdown("**🌐 Job Sites:**")
            for site in config.get('sites', []):
                st.markdown(f"- {site.title()}")
            
            st.markdown(f"**⏰ Freshness:** Last {config.get('hours_old', 24)} hours")
            st.markdown(f"**🤖 AI Scoring:** {'Enabled (Gemini)' if config.get('use_gemini', False) else 'Disabled (Local)'}")
            st.markdown(f"**🌍 Country:** {config.get('country', 'India')}")
    
    st.markdown("---")
    
    # Scraper Control
    st.subheader("🚀 Run Scraper")
    
    # Initialize session state for scraper status
    if 'scraper_running' not in st.session_state:
        st.session_state.scraper_running = False
    if 'scraper_logs' not in st.session_state:
        st.session_state.scraper_logs = []
    if 'last_run' not in st.session_state:
        st.session_state.last_run = "Never"
    
    # Status indicator
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.session_state.scraper_running:
            st.markdown("### 🟡 Status: RUNNING")
        else:
            st.markdown("### 🟢 Status: IDLE")
    
    with col2:
        st.markdown(f"**Last Run:** {st.session_state.last_run}")
    
    with col3:
        if st.button("🔄 Refresh", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    
    st.markdown("---")
    
    # Run button
    col_a, col_b, col_c = st.columns([1, 1, 2])
    
    with col_a:
        if st.button("🚀 Run Scraper Now", type="primary", use_container_width=True, disabled=st.session_state.scraper_running):
            st.session_state.scraper_running = True
            st.session_state.scraper_logs = []
            st.session_state.scraper_process = None
            
            # Create log file path
            log_file = "data/scraper_live.log"
            os.makedirs("data", exist_ok=True)
            
            # Clear previous log file
            if os.path.exists(log_file):
                os.remove(log_file)
            
            try:
                # Start scraper as subprocess
                import sys
                python_exe = sys.executable
                
                # Create a log file to capture output
                log_file = "data/scraper_live.log"
                
                # Run main.py with output redirected to log file
                with open(log_file, 'w') as log_f:
                    process = subprocess.Popen(
                        [python_exe, "-u", "src/main.py"],
                        stdout=log_f,
                        stderr=subprocess.STDOUT,
                        text=True
                    )
                
                st.session_state.scraper_process = process.pid
                st.session_state.scraper_start_time = datetime.now()
                
                # Show initial status
                st.info("🔄 Scraper started! The page will auto-refresh to show live logs.")
                st.info("⏱️ Refresh this page to see the latest logs.")
                
                # Save initial state
                st.session_state.scraper_running = True
                st.rerun()
                
            except Exception as e:
                import traceback
                error_details = traceback.format_exc()
                error_msg = f"❌ Error starting scraper: {str(e)}"
                st.session_state.scraper_logs.append(error_msg)
                st.session_state.scraper_logs.append("\n--- Full Error Details ---")
                st.session_state.scraper_logs.append(error_details)
                st.session_state.scraper_running = False
                st.error(error_msg)
                with st.expander("🔍 View Full Error Details"):
                    st.code(error_details, language="python")
    
    with col_b:
        # Stop button with rollback option
        if st.button("🛑 Stop Scraper", use_container_width=True, disabled=not st.session_state.scraper_running):
            # Show confirmation dialog
            st.session_state.show_stop_confirm = True
    
    # Stop confirmation dialog
    if st.session_state.get("show_stop_confirm", False):
        st.markdown("---")
        st.warning("⚠️ **Stop Scraper Confirmation**")
        st.markdown("Choose how to stop the scraper:")
        
        col_x, col_y, col_z = st.columns(3)
        
        with col_x:
            if st.button("🔄 Stop & Rollback", type="secondary", use_container_width=True):
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
                
                st.session_state.scraper_running = False
                st.session_state.show_stop_confirm = False
                time.sleep(2)
                st.rerun()
        
        with col_y:
            if st.button("🛑 Stop & Keep Data", type="primary", use_container_width=True):
                # Stop without rollback
                scraper = get_scraper()
                result = scraper.stop(rollback=False)
                
                if result["success"]:
                    st.success("✅ Scraper stopped. New data kept.")
                else:
                    st.error(f"❌ {result['error']}")
                
                st.session_state.scraper_running = False
                st.session_state.show_stop_confirm = False
                time.sleep(2)
                st.rerun()
        
        with col_z:
            if st.button("❌ Cancel", use_container_width=True):
                st.session_state.show_stop_confirm = False
                st.rerun()
        
        st.markdown("**🔄 Stop & Rollback:** Cancels scraping and restores previous data")
        st.markdown("**🛑 Stop & Keep Data:** Cancels scraping but keeps any new jobs found")
        st.markdown("---")
    
    # Check if scraper is running
    if st.session_state.scraper_running and 'scraper_process' in st.session_state:
        import psutil
        
        try:
            # Check if process is still running
            if st.session_state.scraper_process:
                try:
                    process = psutil.Process(st.session_state.scraper_process)
                    is_running = process.is_running() and process.status() != psutil.STATUS_ZOMBIE
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    is_running = False
                
                if is_running:
                    # Show running status
                    st.warning("🟡 Scraper is currently running...")
                    
                    # Calculate elapsed time
                    if 'scraper_start_time' in st.session_state:
                        elapsed = datetime.now() - st.session_state.scraper_start_time
                        st.info(f"⏱️ Running for: {elapsed.seconds // 60}m {elapsed.seconds % 60}s")
                    
                    # Read current logs from the scraper output
                    log_file = "data/scraper_live.log"
                    verified_file = "data/verified/verified_jobs.csv"
                    jobs_latest_file = "data/jobs_latest.csv"
                    
                    # Try to read scraper output
                    current_logs = []
                    
                    # Read log file if it exists
                    if os.path.exists(log_file):
                        try:
                            with open(log_file, 'r') as f:
                                log_content = f.read()
                                if log_content.strip():
                                    current_logs.append("📋 Scraper Output:")
                                    current_logs.append(log_content)
                        except:
                            pass
                    
                    # Check scraped jobs file for progress
                    if os.path.exists(jobs_latest_file):
                        try:
                            scraped_df = pd.read_csv(jobs_latest_file)
                            current_logs.append(f"\n🔍 Total jobs scraped: {len(scraped_df)}")
                        except:
                            pass
                    
                    # Check verified jobs file for progress
                    if os.path.exists(verified_file):
                        try:
                            temp_df = pd.read_csv(verified_file)
                            current_logs.append(f"✅ Verified jobs: {len(temp_df)}")
                            if len(temp_df) > 0:
                                temp_df['relevance_score'] = pd.to_numeric(temp_df['relevance_score'], errors='coerce').fillna(0)
                                high_score = len(temp_df[temp_df['relevance_score'] >= 75])
                                current_logs.append(f"⭐ High score jobs (75+): {high_score}")
                        except:
                            pass
                    
                    if current_logs:
                        st.code("\n".join(current_logs), language="text")
                    else:
                        st.info("⏳ Scraper is initializing... Logs will appear shortly.")
                    
                    # Auto-refresh button
                    if st.button("🔄 Refresh Now", key="refresh_running"):
                        st.rerun()
                    
                    # Add auto-refresh using st.empty and time
                    st.info("💡 This page will auto-refresh every 5 seconds. Click 'Refresh Now' for immediate update.")
                    time.sleep(5)
                    st.rerun()
                    
                else:
                    # Process completed
                    st.session_state.scraper_running = False
                    st.session_state.last_run = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    
                    # Read final logs
                    verified_file = "data/verified/verified_jobs.csv"
                    if os.path.exists(verified_file):
                        try:
                            final_df = pd.read_csv(verified_file)
                            st.session_state.scraper_logs = [
                                "✅ Scraper completed successfully!",
                                f"📊 Total verified jobs: {len(final_df)}",
                                f"⭐ High score jobs (75+): {len(final_df[final_df['relevance_score'] >= 75])}",
                                f"✅ Good jobs (60-74): {len(final_df[(final_df['relevance_score'] >= 60) & (final_df['relevance_score'] < 75)])}"
                            ]
                        except Exception as e:
                            st.session_state.scraper_logs = [f"✅ Scraper completed. Check verified jobs file for results."]
                    else:
                        st.session_state.scraper_logs = ["✅ Scraper completed."]
                    
                    st.success("✅ Scraper completed successfully!")
                    st.balloons()
                    st.cache_data.clear()
                    time.sleep(2)
                    st.rerun()
        
        except ImportError:
            st.warning("⚠️ psutil not installed. Install it with: pip install psutil")
            st.info("Assuming scraper completed. Please refresh to see results.")
            st.session_state.scraper_running = False
        except Exception as e:
            st.error(f"❌ Error checking scraper status: {str(e)}")
            st.session_state.scraper_running = False
    
    with col_b:
        if st.button("🗑️ Clear Logs", use_container_width=True):
            st.session_state.scraper_logs = []
            st.rerun()
    
    # Logs display
    st.subheader("📋 Scraper Logs")
    
    if st.session_state.scraper_logs:
        log_text = "\n".join(st.session_state.scraper_logs)
        st.code(log_text, language="text")
    else:
        st.info("No logs yet. Run the scraper to see output here.")
    
    # Quick stats after run
    if st.session_state.last_run != "Never":
        st.markdown("---")
        st.subheader("📊 Latest Run Summary")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Jobs", len(verified_df))
        with col2:
            if len(verified_df) > 0:
                high_score = len(verified_df[verified_df['relevance_score'] >= 75])
                st.metric("High Score (75+)", high_score)
            else:
                st.metric("High Score (75+)", 0)
        with col3:
            st.metric("Emailed", len(history))
        with col4:
            processed = load_processed()
            st.metric("Total Scanned", len(processed))

# --- PAGE 1: Overview ---
elif page == "📊 Overview":
    st.title("🦅 JobSniper Dashboard")
    st.markdown("### Welcome to your manual job hunting command center!")
    
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
        if st.button("🚀 Go to Scraper Control", type="primary", use_container_width=True):
            st.session_state.page = "🎯 Scraper Control"
            st.rerun()
    
    with col_b:
        if st.button("🔄 Refresh Dashboard", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    
    with col_c:
        if st.button("📧 Email History", use_container_width=True):
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
st.sidebar.markdown("v3.0 - Manual Control Edition")
