# GitHub Actions Setup Guide

## Quick Setup (5 minutes)

### Step 1: Add Secrets to GitHub

1. **Go to your repository on GitHub**
   - Navigate to: `https://github.com/YOUR_USERNAME/JobSniper`

2. **Access Settings**
   - Click `Settings` tab (top right)
   - In left sidebar: `Secrets and variables` → `Actions`

3. **Add Required Secrets**
   Click `New repository secret` and add:

   **Secret 1: EMAIL_APP_PASSWORD**
   - Name: `EMAIL_APP_PASSWORD`
   - Value: Your Gmail app password (16 characters)
   
   **Secret 2: GEMINI_API_KEY** (Optional but recommended)
   - Name: `GEMINI_API_KEY`
   - Value: Your Gemini API key
   - Note: Skip if staying 100% free with local analyzer

### Step 2: Enable GitHub Actions

1. **Go to Actions Tab**
   - Click `Actions` in your repository

2. **Enable Workflows**
   - If prompted, click "I understand my workflows, go ahead and enable them"

3. **Verify Workflow**
   - You should see "JobSniper Daily Hunt" workflow
   - Status: Enabled ✅

### Step 3: Test the Workflow

**Option A: Wait for Scheduled Run**
- Workflow runs automatically at 8:00 AM IST daily
- Check back tomorrow morning

**Option B: Manual Test (Recommended)**
1. Go to `Actions` tab
2. Click `JobSniper Daily Hunt` workflow
3. Click `Run workflow` button (right side)
4. Select branch: `main`
5. Click green `Run workflow` button
6. Wait 2-5 minutes
7. Check your email for results!

### Step 4: Monitor Results

**Check Workflow Status:**
1. Actions tab → Click on the running workflow
2. Watch real-time logs
3. Green checkmark ✅ = Success
4. Red X ❌ = Check logs for errors

**Check Your Email:**
- You should receive an email with job matches
- Subject: "🎯 JobSniper: X New Matches"

**Check Repository Updates:**
- Workflow automatically commits updated data files
- Check `data/` folder for new entries

---

## Getting Your Credentials

### Gmail App Password

1. **Go to Google Account**
   - Visit: https://myaccount.google.com/

2. **Enable 2-Step Verification**
   - Security → 2-Step Verification
   - Follow setup wizard

3. **Generate App Password**
   - Search for "App Passwords" in account settings
   - Select app: `Mail`
   - Select device: `Other (Custom name)`
   - Enter: `JobSniper`
   - Click `Generate`
   - **Copy the 16-character password** (e.g., `abcd efgh ijkl mnop`)
   - Remove spaces: `abcdefghijklmnop`

4. **Add to GitHub Secrets**
   - Use this as `EMAIL_APP_PASSWORD`

### Gemini API Key (Optional)

1. **Visit Google AI Studio**
   - Go to: https://aistudio.google.com/app/apikey

2. **Create API Key**
   - Click `Create API Key`
   - Select `Create API key in new project`
   - **Copy the key** (starts with `AIza...`)

3. **Add to GitHub Secrets**
   - Use this as `GEMINI_API_KEY`

4. **Enable in Settings**
   - Edit `config/settings.py`
   - Change `USE_GEMINI = False` to `USE_GEMINI = True`
   - Commit and push changes

**Free Tier Limits:**
- 1,500 requests per day
- 15 requests per minute
- JobSniper uses ~30 requests per run
- **Safe for 1-2 runs daily** ✅

---

## Customizing the Schedule

The workflow runs at **8:00 AM IST** by default.

**To change the time:**

1. **Edit workflow file**
   - Open `.github/workflows/job_sniper.yml`

2. **Find the cron schedule**
   ```yaml
   schedule:
     - cron: '30 2 * * *'  # 8:00 AM IST = 2:30 AM UTC
   ```

3. **Change to your preferred time**
   
   Examples:
   ```yaml
   # 6:00 AM IST (12:30 AM UTC)
   - cron: '30 0 * * *'
   
   # 10:00 AM IST (4:30 AM UTC)
   - cron: '30 4 * * *'
   
   # 8:00 PM IST (2:30 PM UTC)
   - cron: '30 14 * * *'
   ```

4. **Commit and push**
   ```bash
   git add .github/workflows/job_sniper.yml
   git commit -m "Update schedule"
   git push
   ```

**Cron Format:** `minute hour day month weekday`
- All times in UTC (IST = UTC + 5:30)
- Use [crontab.guru](https://crontab.guru/) for help

---

## Troubleshooting

### ❌ Workflow Fails with "Email Failed"

**Cause:** Invalid Gmail app password

**Fix:**
1. Regenerate Gmail app password
2. Update `EMAIL_APP_PASSWORD` secret in GitHub
3. Re-run workflow

### ❌ Workflow Fails with "API Error"

**Cause:** Invalid or missing Gemini API key

**Fix Option 1 (Use Local Analyzer):**
1. Edit `config/settings.py`
2. Set `USE_GEMINI = False`
3. Commit and push

**Fix Option 2 (Fix API Key):**
1. Get new API key from AI Studio
2. Update `GEMINI_API_KEY` secret
3. Re-run workflow

### ❌ No Jobs Found

**Possible Causes:**
- Job sites have no new postings in last 24 hours
- All jobs already processed
- Search queries too specific

**Fixes:**
1. Check if it's a holiday/weekend
2. Wait for next day's run
3. Broaden search queries in `config/settings.py`

### ❌ Workflow Doesn't Run Automatically

**Checks:**
1. Is Actions enabled? (Actions tab)
2. Is workflow file in correct location?
3. Is cron syntax correct?
4. Has repository had recent activity? (GitHub may disable inactive repos)

**Fix:**
- Make a commit to wake up the repository
- Manually run workflow once

### ⚠️ Rate Limit Errors (Gemini API)

**Cause:** Too many API calls

**Fix:**
1. Reduce `RESULTS_WANTED` in settings
2. Run only once per day
3. Or switch to `USE_GEMINI = False`

---

## Advanced Configuration

### Run Multiple Times Per Day

Edit `.github/workflows/job_sniper.yml`:

```yaml
schedule:
  - cron: '30 2 * * *'   # 8:00 AM IST
  - cron: '30 14 * * *'  # 8:00 PM IST
```

**Note:** With Gemini API, limit to 2 runs/day to stay in free tier.

### Run Only on Weekdays

```yaml
schedule:
  - cron: '30 2 * * 1-5'  # Monday to Friday only
```

### Disable Automatic Runs

Comment out the schedule:

```yaml
# schedule:
#   - cron: '30 2 * * *'
workflow_dispatch:  # Keep manual trigger
```

---

## Monitoring API Usage

### Gemini API Dashboard

1. Visit: https://aistudio.google.com/app/apikey
2. Click on your API key
3. View usage statistics
4. Monitor daily quota

### Typical Usage Per Run

- **With Gemini API**: ~30 requests
- **Without Gemini**: 0 requests (100% free)

### Staying Within Free Tier

✅ **Safe Configurations:**
- 1 run/day with Gemini: ~30/1500 quota (2%)
- 2 runs/day with Gemini: ~60/1500 quota (4%)
- Unlimited runs without Gemini: 0 quota used

❌ **Unsafe:**
- 50+ runs/day with Gemini: May exceed quota

---

## Data Persistence

GitHub Actions automatically commits these files after each run:

```
data/
├── history.json              # Jobs already emailed
├── processed.json            # All jobs checked
├── processed_metadata.json   # Timestamps for cleanup
├── Job_Application_Tracker.xlsx
├── raw/jobs_latest.csv
└── verified/verified_jobs.csv
```

**Auto-cleanup:** Jobs older than 7 days are removed from processed list.

---

## Security Best Practices

✅ **Do:**
- Use GitHub Secrets for credentials
- Enable 2FA on GitHub account
- Regularly rotate API keys
- Use app-specific passwords for Gmail

❌ **Don't:**
- Commit `.env` file to repository
- Share API keys publicly
- Use your main Gmail password

---

## Need Help?

1. **Check workflow logs** in Actions tab
2. **Review troubleshooting section** above
3. **Test locally first** with `python src/main.py`
4. **Check GitHub Actions documentation**: https://docs.github.com/en/actions

---

**Setup complete! 🎉**

Your JobSniper will now hunt for jobs automatically every morning while you sleep!
