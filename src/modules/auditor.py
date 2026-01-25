import os
import time
import json
import pandas as pd
import google.generativeai as genai
from google.api_core import exceptions
from config import settings
import re
from dotenv import load_dotenv
from datetime import datetime, timedelta
import sys

# Add database connector
sys.path.insert(0, 'src/modules')
try:
    from db_connector import get_db
    db = get_db()
except:
    db = None
    print("⚠️ Database connector not available, using CSV only")

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

# Files
INPUT_FILE = os.path.join("data", "raw", "jobs_latest.csv")
OUTPUT_FILE = os.path.join("data", "verified", "verified_jobs.csv")
PROFILE_PATH = os.path.join("data", "profile.json")

# NEW: File to track ALL jobs we've ever checked (Good OR Bad)
PROCESSED_LOG = os.path.join("data", "processed.json")
PROCESSED_METADATA_LOG = os.path.join("data", "processed_metadata.json")

MODEL_NAME = "models/gemini-flash-latest"

# Only configure genai if user explicitly allows using the Gemini API
if settings.USE_GEMINI and API_KEY:
    try:
        genai.configure(api_key=API_KEY)
    except Exception:
        print("⚠️ Could not configure Gemini API; falling back to local auditor.")
        settings.USE_GEMINI = False

def load_processed_metadata():
    """Loads metadata about processed jobs including timestamps."""
    if not os.path.exists(PROCESSED_METADATA_LOG):
        return {}
    try:
        with open(PROCESSED_METADATA_LOG, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_processed_metadata(metadata):
    """Saves metadata about processed jobs."""
    with open(PROCESSED_METADATA_LOG, 'w') as f:
        json.dump(metadata, f, indent=2)

def cleanup_old_processed_jobs(days=7):
    """Remove jobs older than specified days from processed list."""
    metadata = load_processed_metadata()
    cutoff_date = datetime.now() - timedelta(days=days)
    
    cleaned_metadata = {}
    removed_count = 0
    
    for url, data in metadata.items():
        processed_date = datetime.fromisoformat(data.get('processed_at', '2020-01-01'))
        if processed_date >= cutoff_date:
            cleaned_metadata[url] = data
        else:
            removed_count += 1
    
    if removed_count > 0:
        save_processed_metadata(cleaned_metadata)
        print(f"🧹 Cleaned {removed_count} old jobs from processed history.")
    
    return list(cleaned_metadata.keys())

def load_processed_urls():
    """Loads the list of URLs we have ALREADY checked in the past."""
    # Clean up old entries first
    return cleanup_old_processed_jobs(days=7)

def save_processed_urls(new_urls):
    """Updates the list of checked URLs with metadata."""
    metadata = load_processed_metadata()
    current_time = datetime.now().isoformat()
    
    for url in new_urls:
        if url not in metadata:
            metadata[url] = {
                'processed_at': current_time,
                'first_seen': current_time
            }
    
    save_processed_metadata(metadata)
    
    # Also maintain the simple list for backward compatibility
    if os.path.exists(PROCESSED_LOG):
        try:
            with open(PROCESSED_LOG, 'r') as f:
                current = json.load(f)
        except:
            current = []
    else:
        current = []
    
    updated = list(set(current + new_urls))
    with open(PROCESSED_LOG, 'w') as f:
        json.dump(updated, f, indent=2)

def load_user_profile():
    try:
        with open(PROFILE_PATH, 'r') as f: return json.load(f)
    except FileNotFoundError: return {"target_role": "AI Intern", "skills": ["Python"]}

def analyze_with_gemini(job_text, location_raw, user_profile):
    # If API usage is disabled, fall back to a local heuristic analyzer.
    if not settings.USE_GEMINI or not API_KEY:
        return analyze_locally(job_text, location_raw, user_profile)

    # (Same function as before)
    truncated_text = str(job_text)[:4000]
    prompt = f"""
    You are an expert Career Auditor. Analyze this job for an AI/ML Student.
    
    CANDIDATE PROFILE: {json.dumps(user_profile)}
    JOB LOCATION (Raw): {location_raw}
    JOB DESCRIPTION: "{truncated_text}"
    
    TASK:
    1. Extract DURATION (e.g., "3 months"). Default "Not Specified".
    2. Determine WORK MODE (Remote/Hybrid/On-site).
    3. SCAM CHECK & RELEVANCE SCORE (0-100).
    
    OUTPUT JSON ONLY:
    {{
        "is_scam": boolean,
        "scam_reason": "string",
        "relevance_score": integer,
        "match_reason": "string",
        "duration": "string",
        "work_mode": "string"
    }}
    """
    model = genai.GenerativeModel(MODEL_NAME)
    retries = 0
    while retries < 3:
        try:
            response = model.generate_content(prompt)
            raw_text = response.text.replace("```json", "").replace("```", "").strip()
            return json.loads(raw_text)
        except exceptions.ResourceExhausted:
            print(f"   ⏳ Rate Limit. Sleeping 60s...")
            time.sleep(60)
            retries += 1
        except Exception as e:
            print(f"   ⚠️ API Error: {e}")
            return None
    return None


def analyze_locally(job_text, location_raw, user_profile):
    """Enhanced local analyzer with better scoring algorithm.

    Returns the same JSON structure expected by the rest of the pipeline.
    """
    text = str(job_text).lower()

    # COMPREHENSIVE SCAM DETECTION
    
    # 1. Payment/Money-related scams
    payment_scams = [
        'pay to apply', 'payment upfront', 'wire transfer', 'send money first',
        'registration fee', 'application fee', 'training fee', 'course fee',
        'pay for training', 'deposit required', 'refundable deposit',
        'guaranteed income', 'quick money', 'earn money fast',
        'investment required', 'pay us', 'payment of', 'fee of',
        'charges apply', 'nominal fee', 'processing fee'
    ]
    
    # 2. Training institutes/academies (not real companies)
    training_institutes = [
        'training institute', 'training academy', 'coaching center',
        'coaching institute', 'learning center', 'skill development center',
        'certification program', 'training program with placement',
        'learn and earn', 'training cum internship', 'paid training',
        'industrial training', 'summer training', 'winter training',
        'educational institute', 'academy internship'
    ]
    
    # 3. Multi-level marketing / Pyramid schemes
    mlm_keywords = [
        'multi-level', 'mlm', 'network marketing', 'direct selling',
        'pyramid', 'referral bonus', 'recruit others', 'build your team',
        'unlimited earning', 'be your own boss', 'work from home earn'
    ]
    
    # 4. Suspicious job characteristics
    suspicious_patterns = [
        'no experience needed earn', 'guaranteed placement after payment',
        'pay after placement but fee first', 'advance payment',
        'security deposit', 'caution money', 'bond amount',
        'work from home no investment but', 'free training but',
        'certificate course with internship', 'internship after course completion'
    ]
    
    # 5. Too-good-to-be-true offers
    unrealistic_offers = [
        'earn lakhs', 'earn thousands daily', 'guaranteed salary',
        'no work high pay', 'easy money', 'instant income',
        'work 2 hours earn', 'part time high income'
    ]
    
    # Combine all scam patterns
    all_scam_patterns = (
        payment_scams + training_institutes + mlm_keywords + 
        suspicious_patterns + unrealistic_offers
    )
    
    # Check for scam patterns
    for pattern in all_scam_patterns:
        if pattern in text:
            # Determine category for better reporting
            if pattern in payment_scams:
                category = "Payment/Fee Required"
            elif pattern in training_institutes:
                category = "Training Institute/Academy"
            elif pattern in mlm_keywords:
                category = "MLM/Network Marketing"
            elif pattern in suspicious_patterns:
                category = "Suspicious Pattern"
            else:
                category = "Unrealistic Offer"
            
            return {
                "is_scam": True,
                "scam_reason": f"🚫 {category}: Contains '{pattern}'",
                "relevance_score": 0,
                "match_reason": "Filtered as potential scam/fake internship.",
                "duration": "Not Specified",
                "work_mode": "Unknown"
            }
    
    # Additional heuristic: Check company name patterns
    company_name = str(location_raw).lower()
    scam_company_patterns = [
        'academy', 'institute', 'training', 'coaching', 'classes',
        'learning center', 'skill development', 'education center'
    ]
    
    # Only flag if it's ONLY a training institute (not a tech company with training division)
    if any(pattern in company_name for pattern in scam_company_patterns):
        # Check if it's a legitimate tech company that also does training
        legit_tech_indicators = [
            'technologies', 'solutions', 'software', 'systems', 'labs',
            'pvt ltd', 'limited', 'corporation', 'inc'
        ]
        
        # If no legit tech indicators, likely just a training institute
        if not any(indicator in company_name for indicator in legit_tech_indicators):
            return {
                "is_scam": True,
                "scam_reason": f"🚫 Training Institute: Company appears to be training/coaching center, not a real employer",
                "relevance_score": 0,
                "match_reason": "Filtered as training institute.",
                "duration": "Not Specified",
                "work_mode": "Unknown"
            }

    # Duration extraction (months/years)
    duration_match = re.search(r"(\d+\s*(?:months|month|years|year))", text)
    duration = duration_match.group(1) if duration_match else "Not Specified"

    # Work mode detection
    if 'remote' in text:
        work_mode = 'Remote'
    elif 'hybrid' in text:
        work_mode = 'Hybrid'
    elif 'on-site' in text or 'onsite' in text or 'office' in text:
        work_mode = 'On-site'
    else:
        work_mode = 'Unknown'

    # IMPROVED SCORING ALGORITHM
    score = 0
    match_reasons = []
    
    # 1. Role matching (40 points max)
    target_role = str(user_profile.get('target_role', '')).lower()
    role_keywords = ['intern', 'internship', 'ai', 'ml', 'machine learning', 'data science', 'deep learning']
    role_matches = sum(1 for kw in role_keywords if kw in text)
    role_score = min(40, role_matches * 10)
    score += role_score
    if role_score > 0:
        match_reasons.append(f"Role keywords matched ({role_matches} found)")
    
    # 2. Skills matching (40 points max)
    skills = user_profile.get('skills', [])
    skill_keywords = [str(s).lower() for s in skills]
    skill_matches = sum(1 for skill in skill_keywords if skill in text)
    skill_score = min(40, skill_matches * 5)
    score += skill_score
    if skill_score > 0:
        match_reasons.append(f"Skills matched: {skill_matches}/{len(skills)}")
    
    # 3. Education level check (10 points)
    if any(word in text for word in ['student', 'undergraduate', 'bachelor', 'btech', 'b.tech']):
        score += 10
        match_reasons.append("Suitable for students")
    
    # 4. Location preference (10 points)
    preferred_locations = user_profile.get('preferences', {}).get('locations', [])
    location_text = str(location_raw).lower()
    if any(loc.lower() in location_text or loc.lower() in text for loc in preferred_locations):
        score += 10
        match_reasons.append("Location matches preferences")
    
    # 5. Bonus for internship-specific terms
    if 'internship' in text or 'intern' in text:
        score += 5
    
    # Ensure minimum score for AI/ML related jobs
    if any(term in text for term in ['artificial intelligence', 'machine learning', 'deep learning', 'neural network', 'pytorch', 'tensorflow']):
        score = max(score, 55)  # Ensure AI/ML jobs get at least 55
        if not match_reasons:
            match_reasons.append("AI/ML related position")
    
    # Cap at 100
    score = min(100, score)
    
    match_reason = "; ".join(match_reasons) if match_reasons else "General match based on profile"

    return {
        "is_scam": False,
        "scam_reason": "",
        "relevance_score": score,
        "match_reason": match_reason,
        "duration": duration,
        "work_mode": work_mode
    }

def run_auditor():
    print("--- 🕵️ Starting AI Auditor (Smart Filter Enabled) ---")
    
    if not os.path.exists(INPUT_FILE):
        print(f"❌ Error: {INPUT_FILE} not found.")
        return

    df = pd.read_csv(INPUT_FILE)
    df = df.dropna(subset=['description'])
    
    if df.empty:
        print("⚠️ No valid jobs found.")
        return

    # ---------------------------------------------------------
    # NEW LOGIC: Filter out ALREADY PROCESSED jobs
    # ---------------------------------------------------------
    processed_urls = load_processed_urls()
    original_count = len(df)
    
    # Keep only jobs where the URL is NOT in our processed list
    df = df[~df['job_url'].isin(processed_urls)]
    
    skipped_count = original_count - len(df)
    if skipped_count > 0:
        print(f"♻️  Skipped {skipped_count} jobs (Already checked previously).")
    
    if df.empty:
        print("✅ All scraped jobs have already been audited. Nothing new to check.")
        return

    profile = load_user_profile()
    verified_jobs = []
    processed_now = [] # Track what we check in this run

    print(f"📂 Auditing {len(df)} NEW jobs...")

    for index, row in df.iterrows():
        print(f"[{index+1}/{len(df)}] {row['title']} @ {row['company']}...")
        
        # Audit
        audit = analyze_with_gemini(row['description'], row.get('location', 'Unknown'), profile)
        
        # Mark as processed immediately so we don't check it again next time
        processed_now.append(row['job_url'])

        # Safety Delay (reduced for efficiency)
        print("   ⏳ Cooling down (2s)...")
        time.sleep(2)

        if audit:
            if not audit['is_scam']:
                row['relevance_score'] = audit['relevance_score']
                row['match_reason'] = audit['match_reason']
                row['duration'] = audit.get('duration', 'Not Specified')
                row['work_mode'] = audit.get('work_mode', 'On-site')
                
                verified_jobs.append(row)
                print(f"   ✅ Verified! Score: {audit['relevance_score']} | {row['work_mode']}")
            else:
                print(f"   ⛔ SCAM: {audit['scam_reason']}")
        else:
            print("   ⚠️ Audit Failed.")

    # Save the "Processed" list so we remember them for tomorrow
    save_processed_urls(processed_now)

    if verified_jobs:
        out_df = pd.DataFrame(verified_jobs).sort_values(by='relevance_score', ascending=False)
        
        # Save to CSV (for backward compatibility)
        out_df.to_csv(OUTPUT_FILE, index=False)
        print(f"\n🎉 Success! Saved {len(out_df)} new jobs to {OUTPUT_FILE}")
        
        # Save to PostgreSQL database
        if db and db.use_database:
            saved_count = 0
            for _, job in out_df.iterrows():
                job_data = {
                    'job_url': job.get('job_url'),
                    'title': job.get('title'),
                    'company': job.get('company'),
                    'location': job.get('location'),
                    'description': job.get('description'),
                    'date_posted': job.get('date_posted'),
                    'relevance_score': job.get('relevance_score'),
                    'match_reason': job.get('match_reason'),
                    'duration': job.get('duration'),
                    'work_mode': job.get('work_mode'),
                    'site': job.get('site')
                }
                if db.insert_verified_job(job_data):
                    saved_count += 1
            print(f"✅ Also saved {saved_count} jobs to PostgreSQL database")
    else:
        print("\n😔 No high-quality jobs found in this batch.")

if __name__ == "__main__":
    run_auditor()