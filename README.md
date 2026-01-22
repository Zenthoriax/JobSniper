# 🦅 JobSniper - Autonomous Job Hunter

An intelligent job scraping and matching system that automatically finds relevant AI/ML internships, scores them against your profile, and emails you the best matches daily.

## 🚀 Features

- **Multi-Platform Scraping**: Searches LinkedIn, Indeed, and Glassdoor
- **Smart Filtering**: AI-powered job matching with relevance scoring
- **Automated Notifications**: Email alerts for high-quality matches
- **Interactive Dashboard**: Streamlit web interface to visualize jobs and analytics
- **GitHub Actions Integration**: Runs automatically every morning at 8 AM IST
- **Duplicate Prevention**: Tracks processed jobs and auto-cleans old entries
- **Excel Tracker**: Maintains application status in organized spreadsheet

## 📋 Recent Optimizations (v2.1)

✅ **Performance Improvements**
- Reduced auditor delay from 20s to 2s per job (10x faster)
- Enhanced local scoring algorithm with multi-factor matching
- Auto-cleanup of processed jobs older than 7 days
- Optimized to fetch only 24-hour fresh jobs

✅ **Better Job Matching**
- Role-based scoring (40 points max)
- Skills matching (40 points max)
- Education level detection (10 points)
- Location preference matching (10 points)
- Minimum score guarantee for AI/ML jobs (55+)

✅ **Automation Ready**
- GitHub Actions workflow configured
- Runs daily at 8 AM IST automatically
- No device needs to be powered on

## 🛠️ Setup Instructions

### 1. Prerequisites
```bash
Python 3.8+
Git
GitHub account
Gmail account (for notifications)
```

### 2. Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/JobSniper.git
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
3. Free tier: 1,500 requests/day (enough for 1-2 runs daily)

#### B. Update your profile:
```bash
python manage_profile.py
```
Or manually edit `data/profile.json` with your skills, target role, and preferences.

### 4. GitHub Actions Setup

#### A. Add Repository Secrets:
1. Go to your GitHub repository
2. Settings → Secrets and variables → Actions
3. Add these secrets:
   - `EMAIL_APP_PASSWORD`: Your Gmail app password
   - `GEMINI_API_KEY`: Your Gemini API key (optional)

#### B. Enable GitHub Actions:
1. Go to Actions tab in your repository
2. Enable workflows if prompted
3. The workflow will run automatically at 8 AM IST daily
4. You can also trigger manually from Actions tab

### 5. Local Testing

```bash
# Run manually to test
cd src
python main.py
```

## 📊 Dashboard

JobSniper now includes an interactive web dashboard built with Streamlit!

### Launch Dashboard
```bash
# From project root
streamlit run dashboard.py
```

The dashboard will open in your browser at `http://localhost:8501`

### Dashboard Features

**📊 Overview Page**
- Quick stats and metrics
- Recent high-scoring jobs
- Activity summary

**💼 Job Listings Page**
- Searchable and filterable job table
- Sort by score, company, or date
- Filter by score range, company, work mode
- Direct apply links

**📋 Application Tracker Page**
- View and manage your applications
- Filter by status (Applied, Interview, Rejected, etc.)
- Track application progress
- Integrated with Excel tracker

**📈 Analytics Page**
- Score distribution histogram
- Top companies hiring (bar chart)
- Work mode breakdown (pie chart)
- Key insights and metrics

**👤 Profile Management Page**
- View and edit your profile
- Update skills, preferences, locations
- Save changes directly to `profile.json`

### Dashboard Screenshots
The dashboard provides a clean, modern interface to:
- Visualize your job search pipeline
- Track application status
- Analyze job market trends
- Manage your profile settings

All data syncs automatically with the main JobSniper system!

## 📊 How It Works

```
┌─────────────┐
│  1. SCRAPE  │ → Searches job sites for AI/ML internships
└──────┬──────┘
       ↓
┌─────────────┐
│  2. AUDIT   │ → Scores jobs against your profile (local or AI)
└──────┬──────┘
       ↓
┌─────────────┐
│  3. FILTER  │ → Keeps only new jobs scoring ≥60
└──────┬──────┘
       ↓
┌─────────────┐
│  4. NOTIFY  │ → Emails you the best matches
└──────┬──────┘
       ↓
┌─────────────┐
│  5. TRACK   │ → Updates Excel tracker
└──────┬──────┘
       ↓
┌─────────────┐
│ 6. DASHBOARD│ → Visualize and manage via web UI
└─────────────┘
```

## ⚙️ Configuration Options

### `config/settings.py`

```python
# Search queries
SEARCH_QUERIES = ["AI Intern", "ML Intern", "Data Science Intern"]

# Locations to search
LOCATIONS = ["Remote", "Bangalore", "Kochi", "Hyderabad", "Chennai"]

# Job freshness (hours)
HOURS_OLD = 24  # Only jobs posted in last 24 hours

# Results per query/location/site
RESULTS_WANTED = 10

# Job sites to scrape
TARGET_SITES = ["linkedin", "indeed", "glassdoor"]

# AI-powered matching (uses API credits)
USE_GEMINI = False  # Set True for better matching
```

## 🎯 Scoring System

### Local Analyzer (No API calls)
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
- **Safe Usage**: 1-2 runs per day

### Monitoring
The system automatically:
- Handles rate limits with retries
- Falls back to local analyzer on errors
- Tracks processed jobs to avoid re-checking

### Cost Control
```python
# Stay 100% free
USE_GEMINI = False  # Uses enhanced local analyzer

# Use free Gemini tier (better results)
USE_GEMINI = True   # ~30 calls/run, safe for daily use
```

## 🗂️ File Structure

```
JobSniper/
├── .github/workflows/
│   └── job_sniper.yml          # GitHub Actions automation
├── config/
│   └── settings.py             # Configuration
├── data/
│   ├── profile.json            # Your profile
│   ├── history.json            # Emailed jobs
│   ├── processed.json          # All checked jobs
│   ├── processed_metadata.json # Timestamps for cleanup
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
│       └── tracker.py          # Excel updates
├── requirements.txt
└── README.md
```

## 🐛 Troubleshooting

### "No jobs found"
- Check if job sites are accessible
- Verify `HOURS_OLD` isn't too restrictive
- Try broader `SEARCH_QUERIES`

### "Email failed"
- Verify Gmail app password is correct
- Check 2-Step Verification is enabled
- Ensure `.env` file exists

### "All jobs already processed"
- This is normal if running multiple times per day
- Jobs are auto-cleaned after 7 days
- Manual cleanup: delete `data/processed_metadata.json`

### GitHub Actions not running
- Check Actions tab is enabled
- Verify secrets are added correctly
- Check workflow file syntax

## 📝 Customization

### Add More Job Sites
Edit `config/settings.py`:
```python
TARGET_SITES = ["linkedin", "indeed", "glassdoor", "zip_recruiter"]
```

### Change Schedule
Edit `.github/workflows/job_sniper.yml`:
```yaml
schedule:
  - cron: '30 2 * * *'  # 8:00 AM IST
  # Change to your preferred time (UTC)
```

### Adjust Match Threshold
Edit `src/modules/notifier.py`:
```python
MIN_MATCH_SCORE = 60  # Lower for more jobs, higher for quality
```

## 🤝 Contributing

Feel free to submit issues and enhancement requests!

## 📜 License

MIT License - feel free to use and modify

## 🙏 Acknowledgments

- Built with [python-jobspy](https://github.com/Bunsly/JobSpy)
- Powered by Google Gemini AI (optional)
- Automated with GitHub Actions

---

**Made with ❤️ for job seekers**

*Last updated: January 2026*
