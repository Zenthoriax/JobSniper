# Scraper Performance Optimization

## Issues Identified

1. **Network Timeouts**
   - LinkedIn timing out on some requests
   - Read timeout errors after 10 seconds

2. **Glassdoor Location Errors**
   - "Remote USA" format not recognized (400 error)
   - "United States Remote" format not recognized

3. **Too Many Combinations**
   - 9 queries × 9 locations × 5 sites = **405 requests**
   - Estimated time: 20-30 minutes
   - High chance of rate limiting

## Optimizations Applied

### 1. Reduced Query Count
**Before:** 9 queries
**After:** 5 queries

```python
# Optimized queries
"AI Intern Remote"           # Covers US + global remote
"Machine Learning Intern Remote"
"Data Science Intern"        # Covers on-site + remote
"AI Intern"
"ML Intern"
```

### 2. Fixed Location Format
**Before:** "Remote USA", "United States Remote" (Glassdoor errors)
**After:** "Remote", "United States" (Glassdoor-friendly)

```python
# Optimized locations
"Remote"              # Works on all sites
"United States"       # Glassdoor-friendly
"Bangalore"
"Hyderabad"
"Chennai"
"Pune"
```

### 3. Reduced Site Count
**Before:** 5 sites (including unreliable Google)
**After:** 4 sites (stable only)

```python
TARGET_SITES = ["linkedin", "indeed", "glassdoor", "zip_recruiter"]
```

### 4. Reduced Results Per Query
**Before:** 10 results
**After:** 8 results

## New Performance Metrics

**Total Requests:**
- 5 queries × 6 locations × 4 sites = **120 requests**
- Estimated time: **5-8 minutes**
- 70% reduction in scraping time!

**Expected Results:**
- ~300-500 unique jobs per run
- ~30-80 quality matches (score ≥55)
- Focus on remote + India tech hubs

## Priority Still Maintained

1. **Remote jobs** (US + global) - searched first
2. **US-based jobs** - "United States" location
3. **India tech hubs** - Bangalore, Hyderabad, Chennai, Pune

## Testing

Run the scraper again:
```bash
cd src
python main.py
```

Should complete in 5-8 minutes without timeouts.
