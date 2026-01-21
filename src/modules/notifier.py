import smtplib
import os
import json
import pandas as pd
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

# --- Configuration ---
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SENDER_EMAIL = "jeevananthan9806@gmail.com"
RECIPIENT_EMAIL = "jeevananthan9806@gmail.com"
SENDER_PASSWORD = os.getenv("EMAIL_APP_PASSWORD") 

VERIFIED_JOBS_FILE = os.path.join("data", "verified", "verified_jobs.csv")
HISTORY_FILE = os.path.join("data", "history.json")

# Lowered threshold to work with enhanced local scoring
MIN_MATCH_SCORE = 55 

def load_history():
    if not os.path.exists(HISTORY_FILE): return []
    try:
        with open(HISTORY_FILE, 'r') as f: return json.load(f)
    except: return []

def save_history(new_urls):
    current_history = load_history()
    updated_history = list(set(current_history + new_urls))
    with open(HISTORY_FILE, 'w') as f:
        json.dump(updated_history, f, indent=2)

def send_email(subject, body):
    try:
        if not SENDER_PASSWORD: return False
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = RECIPIENT_EMAIL
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECIPIENT_EMAIL, msg.as_string())
        server.quit()
        print(f"📧 Email sent to {RECIPIENT_EMAIL}")
        return True
    except Exception as e:
        print(f"❌ Email Failed: {e}")
        return False

def run_notifier():
    print("--- 📨 Starting Notifier (Enhanced Layout) ---")
    
    if not os.path.exists(VERIFIED_JOBS_FILE): return
    df = pd.read_csv(VERIFIED_JOBS_FILE)
    if df.empty: return

    # 1. Filter Score
    df['relevance_score'] = pd.to_numeric(df['relevance_score'], errors='coerce').fillna(0)
    high_value_df = df[df['relevance_score'] >= MIN_MATCH_SCORE]
    
    # 2. Filter History
    history = load_history()
    new_jobs_df = high_value_df[~high_value_df['job_url'].isin(history)]
    
    if new_jobs_df.empty:
        print("✅ No NEW jobs to report.")
        return

    # 3. Build Email
    print(f"🚀 Preparing email for {len(new_jobs_df)} jobs...")
    
    job_rows = ""
    for _, row in new_jobs_df.iterrows():
        score = row['relevance_score']
        color = "#27ae60" if score > 75 else "#d35400" # Green or Orange
        
        # Fallbacks for missing data
        duration = row.get('duration', 'Not Specified')
        work_mode = row.get('work_mode', 'On-site')
        
        job_rows += f"""
        <div style="margin-bottom: 25px; padding: 20px; border: 1px solid #e0e0e0; border-radius: 12px; font-family: sans-serif; background-color: #ffffff;">
            
            <div style="border-bottom: 1px solid #f0f0f0; padding-bottom: 10px; margin-bottom: 10px;">
                <h2 style="margin: 0; color: #2c3e50; font-size: 20px;">{row['title']}</h2>
                <p style="margin: 5px 0; color: #7f8c8d; font-size: 16px;">🏢 <strong>{row['company']}</strong></p>
            </div>

            <div style="display: flex; gap: 15px; margin-bottom: 15px; font-size: 14px;">
                <span style="background-color: #e8f6f3; color: #16a085; padding: 5px 10px; border-radius: 5px;">
                    📍 {work_mode}
                </span>
                <span style="background-color: #fef9e7; color: #f1c40f; padding: 5px 10px; border-radius: 5px;">
                    ⏳ {duration}
                </span>
                <span style="background-color: {color}; color: white; padding: 5px 10px; border-radius: 5px; font-weight: bold;">
                    🎯 Score: {score}/100
                </span>
            </div>

            <div style="background-color: #f9f9f9; padding: 15px; border-radius: 8px; margin-bottom: 15px; color: #444; line-height: 1.5;">
                <strong>💡 Why this matches:</strong><br>
                {row['match_reason']}
            </div>

            <div style="text-align: right;">
                <a href="{row['job_url']}" style="background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 6px; font-weight: bold; font-size: 14px;">
                    Apply Now 🚀
                </a>
            </div>
        </div>
        """

    email_body = f"""
    <html>
    <body style="background-color: #f4f6f8; padding: 20px; font-family: sans-serif;">
        <div style="max-width: 600px; margin: 0 auto; background-color: transparent;">
            <h2 style="text-align: center; color: #2c3e50;">🎯 JobSniper Daily Brief</h2>
            <p style="text-align: center; color: #7f8c8d;">Found <strong>{len(new_jobs_df)}</strong> new matches for you today.</p>
            {job_rows}
            <hr style="border: 0; border-top: 1px solid #ddd; margin-top: 30px;">
            <p style="text-align: center; font-size: 12px; color: #999;">Generated by JobSniper v2.0</p>
        </div>
    </body>
    </html>
    """

    if send_email(f"🎯 JobSniper: {len(new_jobs_df)} New Matches", email_body):
        save_history(new_jobs_df['job_url'].tolist())

if __name__ == "__main__":
    run_notifier()