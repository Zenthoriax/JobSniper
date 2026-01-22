# 🚀 JobSniper Deployment Guide

## Overview
This guide explains how to deploy JobSniper for **24/7 automated job hunting** with a **live dashboard**.

---

## 🎯 Architecture

```
┌─────────────────────────────────────────────────────────┐
│              GITHUB REPOSITORY (Source)                  │
│              github.com/Zenthoriax/JobSniper            │
└─────────────────────────────────────────────────────────┘
                            │
                ┌───────────┴───────────┐
                │                       │
                ▼                       ▼
    ┌───────────────────┐   ┌──────────────────────┐
    │  GITHUB ACTIONS   │   │  STREAMLIT CLOUD     │
    │  (Scraper)        │   │  (Dashboard)         │
    │  FREE ✅          │   │  FREE ✅             │
    └───────────────────┘   └──────────────────────┘
    Runs daily 8 AM IST     Always online 24/7
```

---

## Part 1: Job Scraper Automation (Already Set Up ✅)

### Current Status
- ✅ GitHub Actions workflow configured
- ✅ Runs automatically at 8:00 AM IST daily
- ✅ Scrapes LinkedIn, Indeed, Glassdoor
- ✅ Emails you the best matches
- ✅ Updates database and Excel tracker
- ✅ 100% FREE (uses ~150 min/month of 2,000 free)

### What You Need
Make sure these secrets are added to your GitHub repo:

1. Go to: `https://github.com/Zenthoriax/JobSniper/settings/secrets/actions`
2. Add these secrets:
   - `EMAIL_APP_PASSWORD` - Your Gmail app password
   - `GEMINI_API_KEY` - Your Gemini API key (optional)

### How to Verify It's Working
1. Go to: `https://github.com/Zenthoriax/JobSniper/actions`
2. You should see workflow runs
3. Check your email for daily job alerts

---

## Part 2: Dashboard Deployment (Streamlit Cloud)

### Step 1: Prepare Your Repository

1. **Make sure all code is committed:**
   ```bash
   cd /home/zeno/projects/JobSniper
   git add .
   git commit -m "Added authentication and enhanced tracker"
   git push origin main
   ```

2. **Verify `.gitignore` excludes sensitive data:**
   ```
   .env
   data/*.db
   data/*.json
   data/*.xlsx
   __pycache__/
   *.pyc
   ```

### Step 2: Deploy to Streamlit Cloud

1. **Go to Streamlit Cloud:**
   - Visit: https://share.streamlit.io
   - Click "Sign in with GitHub"
   - Authorize Streamlit to access your repos

2. **Create New App:**
   - Click "New app" button
   - **Repository:** `Zenthoriax/JobSniper`
   - **Branch:** `main`
   - **Main file path:** `dashboard.py`
   - **App URL:** Choose a custom name (e.g., `jobsniper-zenthoriax`)

3. **Click "Deploy!"**
   - Wait 2-3 minutes for deployment
   - Your dashboard will be live!

4. **Access Your Dashboard:**
   - URL: `https://jobsniper-zenthoriax.streamlit.app` (or your chosen name)
   - Login with:
     - **Username:** `zenthoriax`
     - **Password:** `9806`

### Step 3: Configure (Optional)

**Add Secrets (if needed):**
- Go to your app settings
- Add environment variables if you need them for the dashboard

**Custom Domain (Optional):**
- Streamlit Cloud supports custom domains on paid plans
- Free tier uses `*.streamlit.app` subdomain

---

## 🔒 Security Features

### Authentication
- ✅ Password-protected dashboard
- ✅ SHA-256 hashed password (not stored in plaintext)
- ✅ Session-based authentication
- ✅ Logout button in sidebar

### Login Credentials
- **Username:** `zenthoriax`
- **Password:** `9806`

### To Change Password
Edit `dashboard.py` line 17:
```python
VALID_PASSWORD_HASH = hashlib.sha256("YOUR_NEW_PASSWORD".encode()).hexdigest()
```

---

## 📊 How It All Works Together

### Daily Workflow (Automated)

**8:00 AM IST every day:**
1. GitHub Actions wakes up
2. Runs job scraper (`python main.py`)
3. Scrapes jobs from LinkedIn, Indeed, Glassdoor
4. Scores jobs against your profile
5. Sends email with best matches (score ≥55)
6. Updates SQLite database
7. Syncs to Excel tracker
8. Commits changes to GitHub
9. **Dashboard automatically shows new jobs** (reads from GitHub)

### Dashboard Access (24/7)

**Anytime you want:**
1. Visit your dashboard URL
2. Login with credentials
3. View all jobs, update statuses, add notes
4. Changes sync to database and Excel
5. Logout when done

---

## 💰 Cost Breakdown

| Service | Usage | Cost |
|---------|-------|------|
| **GitHub Actions** | ~150 min/month | **FREE** (2,000 min limit) |
| **Streamlit Cloud** | 24/7 hosting | **FREE** (1 app limit) |
| **Gemini API** | ~30 calls/day | **FREE** (1,500/day limit) |
| **Gmail** | Email notifications | **FREE** |
| **Total** | | **$0/month** ✅ |

---

## 🎯 Alternative Deployment Options

### Option 2: Render.com

**Pros:** More resources, custom domains
**Cons:** Spins down after inactivity

**Deploy:**
1. Go to https://render.com
2. Sign in with GitHub
3. New → Web Service
4. Connect `JobSniper` repo
5. Start command: `streamlit run dashboard.py --server.port=$PORT --server.address=0.0.0.0`
6. Deploy!

### Option 3: Railway.app

**Pros:** Fast deployment, $5 free credit/month
**Cons:** Limited free tier

**Deploy:**
1. Go to https://railway.app
2. Sign in with GitHub
3. New Project → Deploy from GitHub
4. Select `JobSniper`
5. Add start command: `streamlit run dashboard.py --server.port=$PORT --server.address=0.0.0.0`
6. Deploy!

---

## 🔧 Troubleshooting

### Dashboard Not Loading
- Check Streamlit Cloud logs
- Verify all dependencies in `requirements.txt`
- Ensure `dashboard.py` is in root directory

### GitHub Actions Failing
- Check Actions tab for error logs
- Verify secrets are added correctly
- Check if job sites are blocking GitHub IPs

### No Jobs Found
- Verify scraper is running (check Actions)
- Check email for notifications
- Adjust `HOURS_OLD` in `config/settings.py` if needed

### Authentication Issues
- Clear browser cache
- Try incognito mode
- Verify credentials are correct

---

## 📱 Mobile Access

Your dashboard works on mobile too!
- Visit the same URL on your phone
- Login with same credentials
- Fully responsive design

---

## 🎉 You're All Set!

### What You Have Now:
✅ Automated job scraping every morning
✅ Email notifications for best matches
✅ 24/7 accessible dashboard
✅ Password-protected access
✅ Interactive application tracking
✅ SQLite database + Excel backup
✅ Analytics and insights
✅ 100% FREE hosting

### Next Steps:
1. Push your code to GitHub
2. Deploy dashboard to Streamlit Cloud
3. Bookmark your dashboard URL
4. Check your email daily for job alerts
5. Update application statuses in dashboard
6. Track your success rate!

---

**Made with ❤️ for job seekers**

*Last updated: January 2026*
