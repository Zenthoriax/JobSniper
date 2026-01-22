# Adding More Job Sites to JobSniper

## ✅ Quick Win: Sites Already Supported by JobSpy

I've already added **ZipRecruiter** to your scraper! JobSpy also supports these sites:

### Currently Active:
- ✅ LinkedIn
- ✅ Indeed
- ✅ Glassdoor
- ✅ **ZipRecruiter** (just added!)

### Available to Add:
- 🌐 **Google Jobs** - Aggregates from multiple sites
- 🇮🇳 **Naukri** - India's largest job site
- 🇦🇪 **Bayt** - Middle East jobs
- 🇧🇩 **BDJobs** - Bangladesh jobs

### How to Add More Supported Sites

Edit `config/settings.py` line 29:

```python
# Add any combination of these:
TARGET_SITES = ["linkedin", "indeed", "glassdoor", "zip_recruiter", "google"]

# For India-specific:
TARGET_SITES = ["linkedin", "indeed", "naukri", "zip_recruiter"]
```

**Note:** More sites = longer scraping time. Current setup with 4 sites takes ~5-10 minutes.

---

## 🛠️ Custom Sites (Jobright, etc.)

For sites NOT supported by JobSpy (like **Jobright**), you need a custom scraper.

### Option 1: Use Jobright's API (if available)

Check if Jobright has a public API:
- Visit: https://jobright.ai/api-docs (if exists)
- Look for API documentation
- Use `requests` library to fetch jobs

### Option 2: Build Custom Web Scraper

**Tools needed:**
- `BeautifulSoup4` or `Scrapy` for HTML parsing
- `Selenium` if site uses JavaScript rendering
- `requests` for HTTP requests

**Example custom scraper structure:**

```python
# src/modules/custom_scrapers/jobright_scraper.py

import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_jobright(search_term, location, results_wanted=10):
    """
    Custom scraper for Jobright.ai
    """
    jobs = []
    
    # Build search URL
    base_url = "https://jobright.ai/jobs"
    params = {
        "q": search_term,
        "l": location,
        "limit": results_wanted
    }
    
    try:
        response = requests.get(base_url, params=params)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Parse job listings (you'll need to inspect Jobright's HTML structure)
        job_cards = soup.find_all('div', class_='job-card')  # Example selector
        
        for card in job_cards:
            job = {
                'title': card.find('h2', class_='job-title').text.strip(),
                'company': card.find('span', class_='company-name').text.strip(),
                'location': card.find('span', class_='location').text.strip(),
                'description': card.find('div', class_='description').text.strip(),
                'job_url': card.find('a')['href'],
                'site': 'jobright'
            }
            jobs.append(job)
        
        return pd.DataFrame(jobs)
    
    except Exception as e:
        print(f"Error scraping Jobright: {e}")
        return pd.DataFrame()
```

### Option 3: Use Selenium for JavaScript-Heavy Sites

If Jobright uses JavaScript to load jobs:

```python
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def scrape_jobright_selenium(search_term, location):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run in background
    driver = webdriver.Chrome(options=options)
    
    try:
        url = f"https://jobright.ai/jobs?q={search_term}&l={location}"
        driver.get(url)
        
        # Wait for jobs to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "job-card"))
        )
        
        # Extract job data
        jobs = []
        job_elements = driver.find_elements(By.CLASS_NAME, "job-card")
        
        for elem in job_elements:
            job = {
                'title': elem.find_element(By.CLASS_NAME, "job-title").text,
                'company': elem.find_element(By.CLASS_NAME, "company").text,
                # ... etc
            }
            jobs.append(job)
        
        return pd.DataFrame(jobs)
    
    finally:
        driver.quit()
```

---

## 🚀 Integration Steps for Custom Scrapers

### 1. Create Custom Scraper Module

```bash
mkdir -p src/modules/custom_scrapers
touch src/modules/custom_scrapers/__init__.py
touch src/modules/custom_scrapers/jobright_scraper.py
```

### 2. Update Main Scraper

Edit `src/modules/scraper.py`:

```python
# Add at top
from custom_scrapers.jobright_scraper import scrape_jobright

# In run_extraction() function, after JobSpy scraping:
def run_extraction():
    all_jobs = []
    
    # ... existing JobSpy code ...
    
    # Add custom scrapers
    print("\n🔧 Running custom scrapers...")
    for query in settings.SEARCH_QUERIES:
        for loc in settings.LOCATIONS:
            try:
                jobright_jobs = scrape_jobright(query, loc, settings.RESULTS_WANTED)
                if not jobright_jobs.empty:
                    all_jobs.append(jobright_jobs)
                    print(f"   ✅ Jobright: {len(jobright_jobs)} jobs")
            except Exception as e:
                print(f"   ❌ Jobright failed: {e}")
    
    # ... rest of existing code ...
```

### 3. Add Dependencies

Update `requirements.txt`:

```
# For BeautifulSoup
beautifulsoup4
lxml

# For Selenium (if needed)
selenium
webdriver-manager
```

---

## ⚠️ Important Considerations

### Legal & Ethical
- ✅ Check site's `robots.txt` and Terms of Service
- ✅ Respect rate limits (add delays between requests)
- ✅ Don't overload servers
- ✅ Use for personal job search only

### Technical Challenges
- 🔄 Sites change HTML structure frequently (scrapers break)
- 🤖 Anti-bot protection (CAPTCHA, IP blocking)
- ⏱️ Slower than APIs (need to parse HTML)
- 🛠️ Maintenance required when sites update

### Recommendation
**For Jobright specifically:**
1. Check if they have an API or RSS feed
2. If not, use Selenium-based scraper
3. Add generous delays (5-10 seconds between requests)
4. Run less frequently to avoid detection

---

## 🎯 My Recommendation

**For now:**
1. ✅ Use the 4 sites I've configured (LinkedIn, Indeed, Glassdoor, ZipRecruiter)
2. ✅ Test with `python src/main.py` to see if you get good results
3. ⏸️ Only add custom scrapers if you're not getting enough jobs

**If you need Jobright:**
1. Inspect their website structure
2. Build a custom scraper (I can help!)
3. Test locally before adding to automation
4. Monitor for changes

---

## 📝 Next Steps

Want me to:
1. **Add Google Jobs** to your current setup? (easy, 1 line change)
2. **Build a custom Jobright scraper**? (needs research on their site structure)
3. **Add Naukri** for more India-specific jobs? (easy, 1 line change)

Let me know which sites you want to prioritize!
