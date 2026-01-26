# Deployment Checklist for JobSniper

## Pre-Deployment Verification ✅

- [x] Supabase database connection working
- [x] All CRUD operations tested
- [x] Excel sync functional
- [x] Environment variables configured
- [x] Dashboard connection indicator working
- [x] All 38 jobs migrated successfully
- [x] SQLite removed, backup created
- [x] Python syntax validated

## Deployment Options

### Option 1: Streamlit Cloud (Recommended)

**Pros:**
- Free tier available
- Easy deployment from GitHub
- Automatic HTTPS
- Built-in secrets management

**Steps:**
1. Push code to GitHub repository
2. Go to https://share.streamlit.io
3. Connect your GitHub account
4. Select repository and branch
5. Set `dashboard.py` as main file
6. Add secrets in Streamlit Cloud dashboard:
   ```
   SUPABASE_URL = "your-url"
   SUPABASE_KEY = "your-key"
   DASHBOARD_USERNAME = "your-username"
   DASHBOARD_PASSWORD = "your-password"
   GEMINI_API_KEY = "your-api-key"
   EMAIL_APP_PASSWORD = "your-email-password"
   DASHBOARD_SECRET_KEY = "your-secret-key"
   ```
7. Deploy!

### Option 2: Render

**Pros:**
- Free tier with 750 hours/month
- Auto-deploy from GitHub
- Custom domains

**Steps:**
1. Create `render.yaml` (already provided)
2. Push to GitHub
3. Connect Render to your repository
4. Add environment variables in Render dashboard
5. Deploy

### Option 3: Railway

**Pros:**
- $5 free credit monthly
- Simple deployment
- Good performance

**Steps:**
1. Install Railway CLI or use web dashboard
2. Connect GitHub repository
3. Add environment variables
4. Deploy with one click

## Required Environment Variables

Make sure these are set in your deployment platform:

```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
DASHBOARD_USERNAME=your-username
DASHBOARD_PASSWORD=your-password
DASHBOARD_SECRET_KEY=your-secret-key
GEMINI_API_KEY=your-api-key (optional, for AI scoring)
EMAIL_APP_PASSWORD=your-email-password (optional, for notifications)
```

## Files Ready for Deployment

- ✅ `dashboard.py` - Main application
- ✅ `requirements.txt` - Dependencies
- ✅ `src/modules/db_manager.py` - Database layer
- ✅ `.env` - Local environment (DO NOT commit to GitHub)
- ✅ `.gitignore` - Configured to exclude sensitive files
- ✅ `README.md` - Documentation

## Security Checklist

- [ ] Remove `.env` from repository (add to `.gitignore`)
- [ ] Use strong passwords for dashboard
- [ ] Rotate Supabase keys if exposed
- [ ] Enable Row Level Security in Supabase
- [ ] Use environment variables for all secrets

## Post-Deployment Testing

After deployment, test:
1. Dashboard loads correctly
2. Login works
3. Database connection indicator shows green
4. Can view jobs in Application Tracker
5. Can update job status
6. Excel sync works
7. Scraper control functions

## Troubleshooting

**Connection Error:**
- Check Supabase credentials
- Verify Supabase project is active
- Check network/firewall settings

**Login Issues:**
- Verify DASHBOARD_USERNAME and DASHBOARD_PASSWORD
- Clear browser cache
- Check session timeout settings

**Missing Data:**
- Verify Supabase table exists
- Check RLS policies
- Ensure migration completed

## Next Steps After Deployment

1. Test all functionality
2. Set up GitHub Actions for automated scraping (optional)
3. Configure custom domain (optional)
4. Set up monitoring/alerts
5. Create backup schedule

---

**Ready to Deploy!** 🚀

Choose your deployment platform and follow the steps above.
