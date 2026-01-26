# Streamlit Cloud Deployment - Step by Step

## ✅ Pre-Deployment Checklist Complete
- [x] Code validated
- [x] Database migrated to Supabase
- [x] All tests passing
- [x] Documentation complete

## 🚀 Deployment Steps

### Step 1: Prepare Repository

First, let's make sure your code is ready for GitHub:

```bash
# Check git status
git status

# Add all files
git add .

# Commit changes
git commit -m "v4.0: Supabase migration complete - ready for Streamlit Cloud"

# Push to GitHub
git push origin main
```

### Step 2: Create Streamlit Cloud Account

1. Go to https://share.streamlit.io
2. Click "Sign up" or "Continue with GitHub"
3. Authorize Streamlit to access your GitHub account

### Step 3: Deploy Your App

1. Click "New app" button
2. Select your repository: `Zenthoriax/JobSniper`
3. Select branch: `main`
4. Set main file path: `dashboard.py`
5. Click "Advanced settings"

### Step 4: Configure Secrets

In the "Secrets" section, paste this (replace with your actual values):

```toml
# Supabase Configuration
SUPABASE_URL = "https://fikplzrbnpyufoxqkhvu.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZpa3BsenJibnB5dWZveHFraHZ1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk0MTkzMzEsImV4cCI6MjA4NDk5NTMzMX0.qQsi_4xJmbn83HgkznxStnP-E4QmwBr70rfe3_H1Qic"

# Dashboard Authentication
DASHBOARD_USERNAME = "zenthoriax"
DASHBOARD_PASSWORD = "9806"
DASHBOARD_SECRET_KEY = "jobsniper_secret_key_2026_secure_random_string"

# Optional Features
GEMINI_API_KEY = "AIzaSyDLONBkKJ1ayGJ78SK7mDfm7IsnQx8Dy_I"
EMAIL_APP_PASSWORD = "iseh nxil cznu jhvi"
```

### Step 5: Deploy!

1. Click "Deploy!" button
2. Wait for deployment (usually 2-3 minutes)
3. Your app will be live at: `https://your-app-name.streamlit.app`

### Step 6: Test Deployment

Once deployed, test:
- [ ] Dashboard loads
- [ ] Login works
- [ ] Connection indicator shows green 🟢
- [ ] Can view jobs in Application Tracker
- [ ] Can update job status
- [ ] Scraper control works

## 🎯 Your App URL

After deployment, you'll get a URL like:
```
https://jobsniper.streamlit.app
```

You can customize this in Streamlit Cloud settings.

## 🔧 Troubleshooting

**If deployment fails:**
1. Check the logs in Streamlit Cloud dashboard
2. Verify all secrets are set correctly
3. Make sure `requirements.txt` is up to date
4. Check that `dashboard.py` is in the root directory

**If connection indicator is red:**
1. Verify Supabase credentials in secrets
2. Check Supabase project is active
3. Verify RLS policies are set correctly

**If login doesn't work:**
1. Check DASHBOARD_USERNAME and DASHBOARD_PASSWORD in secrets
2. Clear browser cache and try again

## 📱 Next Steps After Deployment

1. **Custom Domain** (optional)
   - Go to app settings in Streamlit Cloud
   - Add your custom domain

2. **Share Your App**
   - Share the URL with others
   - All data is in Supabase cloud (accessible from anywhere)

3. **Monitor Usage**
   - Check Streamlit Cloud analytics
   - Monitor Supabase database usage

4. **Updates**
   - Just push to GitHub
   - Streamlit Cloud auto-deploys changes

---

**Ready to deploy!** Follow the steps above and your JobSniper will be live in minutes! 🚀
