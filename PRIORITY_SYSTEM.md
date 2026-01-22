# JobSniper Priority Configuration

## 🎯 Search Priority System

JobSniper is now configured with a **3-tier priority system** for maximum flexibility:

### Priority 1: 🇺🇸 US-Based Remote Internships
- **Search queries:** "AI Intern Remote USA", "ML Intern Remote USA", etc.
- **Locations:** "Remote USA", "United States Remote"
- **Why:** Best opportunities for international students, competitive pay, global experience

### Priority 2: 🌐 Global Remote Internships
- **Search queries:** "AI Intern Remote", "ML Intern Remote", etc.
- **Locations:** "Remote"
- **Why:** Flexible, work from anywhere, diverse companies

### Priority 3: 🇮🇳 India Tech Hubs (On-site)
- **Search queries:** "AI Intern", "ML Intern", etc.
- **Locations:** Bangalore, Kochi, Hyderabad, Chennai, Pune, Mumbai
- **Why:** Local opportunities, easier visa/logistics, growing tech scene

---

## 📋 Current Configuration

### Search Queries (9 total)
```python
# US Remote (Priority 1)
"AI Intern Remote USA"
"Machine Learning Intern Remote USA"
"Data Science Intern Remote USA"

# Global Remote (Priority 2)
"AI Intern Remote"
"Machine Learning Intern Remote"
"Data Science Intern Remote"

# On-site (Priority 3)
"AI Intern"
"Machine Learning Intern"
"Data Science Intern"
```

### Locations (9 total)
```python
# US Remote (Priority 1)
"Remote USA"
"United States Remote"

# Global Remote (Priority 2)
"Remote"

# India On-site (Priority 3)
"Bangalore"
"Kochi"
"Hyderabad"
"Chennai"
"Pune"
"Mumbai"
```

### Job Sites (5 total)
- LinkedIn
- Indeed
- Glassdoor
- ZipRecruiter
- Google Jobs

---

## 🔢 Expected Job Volume

**Calculation:**
- 9 search queries × 9 locations × 5 sites × 10 results = **4,050 potential jobs**
- After deduplication: ~500-1000 unique jobs per day
- After filtering (score ≥55): ~50-200 quality matches

**Breakdown by priority:**
1. **US Remote:** ~20-50 jobs (highest quality, competitive)
2. **Global Remote:** ~30-80 jobs (diverse, flexible)
3. **India On-site:** ~100-200 jobs (most volume, local)

---

## 💡 How the Scraper Works

### Step 1: Scraping Order
The scraper processes in this order:
1. "AI Intern Remote USA" + "Remote USA" → US remote jobs
2. "AI Intern Remote USA" + "United States Remote" → More US remote
3. "AI Intern Remote" + "Remote" → Global remote
4. "AI Intern" + "Bangalore" → India on-site
5. ... and so on

### Step 2: Scoring
The auditor scores jobs based on:
- **Role match** (40 pts): Keywords like "AI", "ML", "intern"
- **Skills match** (40 pts): Your skills (Python, TensorFlow, etc.)
- **Education** (10 pts): Student-friendly positions
- **Location** (10 pts): Matches your preferences
- **Bonus** (+5-15 pts): Remote work, AI/ML specific

### Step 3: Filtering
- **Minimum score:** 55/100
- **Scam detection:** Filters out fake jobs, training institutes
- **Duplicate removal:** Same company + role = one entry

### Step 4: Email Notification
You'll receive emails with:
- Jobs scoring ≥55
- Sorted by score (highest first)
- US remote jobs will naturally score higher (location match)

---

## 🎓 Visa & Work Authorization

### US Remote Internships
Most require one of:
- ✅ F-1 CPT/OPT (for students in US)
- ✅ H-1B visa
- ✅ Green Card
- ✅ US Citizenship
- ⚠️ Some offer visa sponsorship for exceptional candidates

**Look for keywords:**
- "Open to international students"
- "F-1 CPT/OPT eligible"
- "Visa sponsorship available"
- "Remote from anywhere"

### Global Remote
- Usually more flexible
- May not require US work authorization
- Check company's country and policies

### India On-site
- No visa needed (you're in India)
- Easier logistics
- Local networking opportunities

---

## 📊 Optimization Tips

### To Get More US Remote Jobs:
1. Set `USE_GEMINI = True` in settings (better matching)
2. Increase `RESULTS_WANTED` to 15-20
3. Add more US-specific search terms
4. Apply early (US companies move fast)

### To Reduce Noise:
1. Increase minimum score threshold in `notifier.py`
2. Reduce `RESULTS_WANTED` to 5-8
3. Focus on fewer locations
4. Enable scam detection (already on)

### To Balance Speed vs Coverage:
- **Current:** 9 queries × 9 locations × 5 sites = ~5-10 min runtime
- **Faster:** Reduce to 6 queries × 6 locations = ~3-5 min
- **More coverage:** Increase `RESULTS_WANTED` = ~10-15 min

---

## 🚀 Next Steps

1. **Test the configuration:**
   ```bash
   cd src
   python main.py
   ```

2. **Check results:**
   - Look at `data/verified/verified_jobs.csv`
   - Check your email for notifications
   - Review dashboard for job distribution

3. **Adjust if needed:**
   - Too many India jobs? Remove some locations
   - Not enough US remote? Add more US-specific queries
   - Too slow? Reduce locations or sites

---

## 📝 Summary

✅ **3-tier priority system** (US Remote → Global Remote → India On-site)
✅ **9 search queries** covering all priorities
✅ **9 locations** from US to India
✅ **5 job sites** for maximum coverage
✅ **Smart scoring** prioritizes remote + your skills
✅ **Scam filtering** removes fake jobs
✅ **Daily automation** via GitHub Actions

**You're all set to find the perfect internship!** 🎯
