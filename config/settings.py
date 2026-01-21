import os

# --- Search Configuration ---
SEARCH_QUERIES = [
    "AI Intern", 
    "Machine Learning Intern", 
    "Data Science Intern",
    "Deep Learning Intern",
    "ML Research Intern",
    "AI Research Intern"
]
# Removed "Deep Learning" etc for now to speed up the test. 
# Once this works, you can add them back.

COUNTRY = 'India' 

# NOW WE USE ALL OF THESE:
LOCATIONS = ["Remote", "Bangalore", "Kochi", "Hyderabad", "Chennai"]

# --- Scraper Settings ---
# Reduced to 24 hours to get fresher jobs and avoid duplicates
HOURS_OLD = 24 

# Lower this to 10.
# Why? 3 Queries * 5 Locations * 3 Sites * 10 Jobs = 450 potential requests.
# 10 is plenty per slot.
RESULTS_WANTED = 10

TARGET_SITES = ["linkedin", "indeed", "glassdoor"]

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