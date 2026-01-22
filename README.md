# 🦅 JobSniper - Manual Job Hunter

An intelligent job scraping and matching system that finds relevant AI/ML internships, scores them against your profile, and emails you the best matches - all controlled manually through an interactive dashboard.

## 🚀 Features

- **Multi-Platform Scraping**: Searches LinkedIn, Indeed, Glassdoor, Zip Recruiter, and Google Jobs
- **Smart Filtering**: AI-powered job matching with relevance scoring (local or Gemini AI)
- **Manual Control**: Run scraping on-demand from the dashboard whenever you want
- **Email Notifications**: Get email alerts for high-quality matches
- **Interactive Dashboard**: Streamlit web interface with 6 pages
  - 🎯 Scraper Control - Run jobs manually with real-time logs
  - 📊 Overview - Quick stats and recent jobs
  - 💼 Job Listings - Searchable and filterable job table
  - 📋 Application Tracker - Manage applications with SQLite + Excel sync
  - 📈 Analytics - Visualize job market trends
  - 👤 Profile - Manage your skills and preferences
- **Duplicate Prevention**: Tracks processed jobs and auto-cleans old entries
- **Dual Storage**: SQLite database + Excel tracker for compatibility

## 📋 What's New in v3.0

✅ **Manual Control**
- Removed automated GitHub Actions workflow
- All scraping now done manually through dashboard
- Real-time log viewer to monitor scraping progress
- Status indicators (Idle/Running/Completed)

✅ **Enhanced Dashboard**
- New "Scraper Control" page as primary interface
- Configuration display showing current settings
- One-click scraping with progress monitoring
- Auto-refresh after scraping completes

✅ **Better Job Matching**
- Role-based scoring (40 points max)
- Skills matching (40 points max)
- Education level detection (10 points)
- Location preference matching (10 points)
- Minimum score guarantee for AI/ML jobs (55+)
- Optional Gemini AI for semantic understanding

## 🛠️ Setup Instructions

### 1. Prerequisites
```bash
Python 3.8+
Gmail account (for notifications)
```

### 2. Installation

```bash
# Clone the repository
git clone https://github.com/Zenthoriax/JobSniper.git
cd JobSniper

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

#### A. Create `.env` file in project root:
```env
EMAIL_APP_PASSWORD=your_gmail_app_password
GEMINI_API_KEY=your_gemini_api_key  # Optional, for AI-powered matching
```

**Getting Gmail App Password:**
1. Go to Google Account → Security
2. Enable 2-Step Verification
3. Search for "App Passwords"
4. Generate password for "Mail"
5. Copy the 16-character password

**Getting Gemini API Key (Optional):**
1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Create new API key
3. Free tier: 1,500 requests/day

#### B. Update your profile:
```bash
python manage_profile.py
```
Or manually edit `data/profile.json` with your skills, target role, and preferences.

### 4. Launch Dashboard

```bash
# From project root
streamlit run dashboard.py
```

The dashboard will open in your browser at `http://localhost:8501`

**Login Credentials:**
- Username: `zenthoriax`
- Password: `9806`

## 📊 How to Use

### Running Your First Job Search

1. **Launch Dashboard**
   ```bash
   streamlit run dashboard.py
   ```

2. **Login** with your credentials

3. **Go to "🎯 Scraper Control" page**
   - View current configuration (sites, queries, locations)
   - Click "🚀 Run Scraper Now" button
   - Watch real-time logs as jobs are scraped and scored
   - Wait for completion (usually 2-5 minutes)

4. **Check Your Email** for job matches (score ≥55)

5. **View Jobs** in other dashboard pages:
   - 📊 Overview - See recent high-score jobs
   - 💼 Job Listings - Browse all jobs with filters
   - 📋 Application Tracker - Update application statuses

6. **Run Again** whenever you want to find new jobs!

## 📊 Dashboard Pages

### 🎯 Scraper Control (Primary Page)
- **Configuration Display**: See current search queries, locations, job sites
- **Run Button**: Start scraping manually
- **Status Indicator**: Shows Idle/Running/Completed
- **Real-time Logs**: Watch scraping progress
- **Summary Stats**: Jobs found, high scores, emails sent

### 📊 Overview
- Quick metrics and stats
- Recent high-scoring jobs
- Quick actions (refresh, email history)

### 💼 Job Listings
- Searchable and filterable job table
- Sort by score, company, or date
- Filter by score range, company, work mode
- Expandable job cards with details
- Direct apply links

### 📋 Application Tracker
- View and manage your applications
- Filter by status (Applied, Interview, Rejected, etc.)
- Add notes to each application
- Update status with dropdown
- Syncs to both SQLite database and Excel

### 📈 Analytics
- Score distribution histogram
- Top companies hiring (bar chart)
- Work mode breakdown (pie chart)
- Key insights and metrics

### 👤 Profile Management
- View and edit your profile
- Update skills, preferences, locations
- Save changes directly to `profile.json`

## ⚙️ Configuration Options

### `config/settings.py`

```python
# Search queries
SEARCH_QUERIES = [
    "AI Intern Remote",
    "Machine Learning Intern Remote",
    "Data Science Intern Remote",
    "AI Intern",
    "ML Intern",
    "Data Science Intern"
]

# Locations to search
LOCATIONS = ["Remote", "Bangalore", "Kochi", "Chennai", "Hyderabad", "Pune"]

# Country
COUNTRY = 'India'

# Job freshness (hours)
HOURS_OLD = 24  # Only jobs posted in last 24 hours

# Results per query/location/site
RESULTS_WANTED = 10

# Job sites to scrape (5 total!)
TARGET_SITES = [
    "linkedin",        # Professional network
    "indeed",          # Largest job board
    "glassdoor",       # Company reviews + jobs
    "zip_recruiter",   # Good for remote jobs
    "google"           # Google Jobs aggregator
]

# AI-powered matching (uses API credits)
USE_GEMINI = False  # Set True for better matching
```

## 🎯 Scoring System

### Local Analyzer (No API calls - Default)
- **Role Keywords** (40 pts): intern, AI, ML, data science, etc.
- **Skills Match** (40 pts): Python, TensorFlow, PyTorch, etc.
- **Education Level** (10 pts): student, undergraduate, B.Tech
- **Location Match** (10 pts): matches your preferences
- **Bonus**: AI/ML jobs guaranteed minimum 55 points

### Gemini Analyzer (Optional)
- Deep semantic understanding of job descriptions
- Context-aware skill matching
- Scam detection with reasoning
- More accurate relevance scoring

## 📧 Email Notifications

You'll receive beautifully formatted emails with:
- Job title and company
- Work mode (Remote/Hybrid/On-site)
- Duration
- Relevance score with color coding
- Match reasoning
- Direct apply links

## 📈 Excel Tracker

Automatically maintained at `data/Job_Application_Tracker.xlsx`:
- Date found
- Company & role
- Location & duration
- Match score
- Application status (dropdown)
- Direct link to posting

## 🔒 API Credit Safety

### Free Tier Limits
- **Gemini API**: 1,500 requests/day, 15/minute
- **Typical Run**: ~30 API calls
- **Safe Usage**: Multiple runs per day possible

### Monitoring
The system automatically:
- Handles rate limits with retries
- Falls back to local analyzer on errors
- Tracks processed jobs to avoid re-checking

### Cost Control
```python
# Stay 100% free (recommended)
USE_GEMINI = False  # Uses enhanced local analyzer

# Use free Gemini tier (better results)
USE_GEMINI = True   # ~30 calls/run, safe for daily use
```

## 🗂️ File Structure

```
JobSniper/
├── config/
│   └── settings.py             # Configuration
├── data/
│   ├── profile.json            # Your profile
│   ├── history.json            # Emailed jobs
│   ├── processed.json          # All checked jobs
│   ├── processed_metadata.json # Timestamps for cleanup
│   ├── job_tracker.db          # SQLite database
│   ├── Job_Application_Tracker.xlsx
│   ├── raw/
│   │   └── jobs_latest.csv     # Scraped jobs
│   └── verified/
│       └── verified_jobs.csv   # Scored jobs
├── src/
│   ├── main.py                 # Entry point
│   └── modules/
│       ├── scraper.py          # Job scraping
│       ├── auditor.py          # Job scoring
│       ├── notifier.py         # Email alerts
│       ├── tracker.py          # Excel updates
│       └── db_manager.py       # SQLite operations
├── dashboard.py                # Streamlit dashboard
├── requirements.txt
└── README.md
```

## 🐛 Troubleshooting

### "No jobs found"
- Check if job sites are accessible
- Verify `HOURS_OLD` isn't too restrictive (try 48 or 72)
- Try broader `SEARCH_QUERIES`
- Check scraper logs in dashboard

### "Email failed"
- Verify Gmail app password is correct
- Check 2-Step Verification is enabled
- Ensure `.env` file exists in project root

### "All jobs already processed"
- This is normal if running multiple times per day
- Jobs are auto-cleaned after 7 days
- Manual cleanup: delete `data/processed_metadata.json`

### Dashboard not loading
- Check if Streamlit is installed: `pip install streamlit`
- Verify you're in the project root directory
- Try: `streamlit run dashboard.py --server.port 8502`

### Authentication issues
- Default username: `zenthoriax`
- Default password: `9806`
- To change: Edit `dashboard.py` line 17

## 📝 Customization

### Add More Job Sites
Edit `config/settings.py`:
```python
TARGET_SITES = ["linkedin", "indeed", "glassdoor", "zip_recruiter", "google"]
```

### Adjust Match Threshold
Edit `src/modules/notifier.py`:
```python
MIN_MATCH_SCORE = 60  # Lower for more jobs, higher for quality
```

### Change Dashboard Password
Edit `dashboard.py`:
```python
VALID_USERNAME = "your_username"
VALID_PASSWORD_HASH = hashlib.sha256("your_password".encode()).hexdigest()
```

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

## 📜 License

MIT License - feel free to use and modify

## 🙏 Acknowledgments

- Built with [python-jobspy](https://github.com/Bunsly/JobSpy)
- Powered by Google Gemini AI (optional)
- Dashboard built with Streamlit

---

**Made with ❤️ for job seekers**

*Last updated: January 2026 - v3.0 Manual Control Edition*
