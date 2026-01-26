import os

# --- Search Configuration ---
# Broader search queries to capture more opportunities
SEARCH_QUERIES = [
    "AI Intern",
    "Machine Learning Intern",
    "Data Science Intern",
    "ML Intern",
    "Artificial Intelligence Intern",
    "Deep Learning Intern",
    "AI/ML Intern",
    "Data Analyst Intern",
    "Python Developer Intern",
    "Software Engineer Intern AI"
]

# India for local opportunities
COUNTRY = 'India' 

# Expanded locations for more coverage
LOCATIONS = [
    "Remote",              # Priority 1: Remote (global)
    "India",               # Broad India search
    "Bangalore",           # Tech hubs
    "Mumbai",
    "Hyderabad", 
    "Pune",
    "Delhi",
    "Chennai"
]

# --- Scraper Settings ---
# Increased time window to find more jobs
HOURS_OLD = 168  # 7 days (was 72) - much wider window

# Increased results per query
RESULTS_WANTED = 50  # Increased from 20 to 50 for maximum discovery

# Job sites - only working ones
# Note: Glassdoor and ZipRecruiter disabled due to 403 blocking
TARGET_SITES = [
    "linkedin",        # Professional network - Working
    "indeed",          # Largest job board - Working  
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