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

# Job sites to scrape
# Note: Some sites may block automated requests (403 errors)
# Glassdoor and ZipRecruiter currently blocked - disabled
TARGET_SITES = [
    "linkedin",        # Professional network - Working
    "indeed",          # Largest job board - Working  
    # "glassdoor",     # DISABLED - Returns 403 errors
    # "zip_recruiter", # DISABLED - Returns 403 errors
    "google"           # Google Jobs aggregator - Working
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