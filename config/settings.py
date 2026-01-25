import os

# --- Search Configuration ---
# Focus on remote opportunities and India tech hubs
SEARCH_QUERIES = [
    "AI Intern Remote",
    "Machine Learning Intern Remote",
    "Data Science Intern Remote",
    "AI Intern",
    "ML Intern",
    "Data Science Intern"
]

# India for local opportunities
COUNTRY = 'India' 

# Priority: Remote first, then India tech hubs
LOCATIONS = [
    "Remote",              # Priority 1: Remote (global, includes US)
    "Bangalore",           # Priority 2: India tech hubs
    "Kochi",
    "Chennai",
    "Hyderabad", 
    "Pune"
]

# --- Scraper Settings ---
HOURS_OLD = 72  # Increased from 24 to 72 for wider time window

# Results per query/location/site
RESULTS_WANTED = 20  # Increased from 10 to 20 for more job discovery

# JobSpy supported sites (5 total for maximum coverage!)
# Note: Google/Microsoft company career pages need custom scrapers
# But these sites already show Google/Microsoft job postings
TARGET_SITES = [
    "linkedin",        # Professional network, has Google/MS jobs
    "indeed",          # Largest job board, has Google/MS jobs
    "glassdoor",       # Company reviews + salaries + jobs
    "zip_recruiter",   # Good for remote jobs
    "google"           # Google Jobs (aggregates from multiple sources including Google Careers!)
]

# --- Runtime flags ---
# When False, the auditor will use an enhanced local rule-based scorer (no API calls).
# Set to True to use Gemini API for better matching (stays within free tier at 1-2 runs/day).
# Free tier: 15 requests/min, 1,500 requests/day
USE_GEMINI = False  # Set to True for better job matching with AI

# Rotate and randomize queries/locations per run to surface varied jobs
ROTATE_QUERIES = True
RANDOMIZE_LOCATIONS = True

# ... (Rest of file stays the same) ...
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data", "raw")
VERIFIED_DIR = os.path.join(BASE_DIR, "data", "verified")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(VERIFIED_DIR, exist_ok=True)