import os
import google.generativeai as genai
from dotenv import load_dotenv

# 1. Load Environment
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

print("--- 🔍 JobSniper Diagnostic Tool ---")

# 2. Check Key Format
if not api_key:
    print("❌ ERROR: API Key is Missing! Check your .env file.")
    exit()

print(f"🔑 Key found: {api_key[:5]}...{api_key[-4:]}")
print(f"   Length: {len(api_key)} characters")

if '"' in api_key or "'" in api_key:
    print("⚠️ WARNING: Your key contains quotes inside the string. Remove them in .env!")
    # Auto-fix for testing
    api_key = api_key.replace('"', '').replace("'", '')
    print(f"   (Auto-corrected key for this test)")

# 3. Configure API
genai.configure(api_key=api_key)

# 4. List Available Models
print("\n📡 Connecting to Google Servers...")
try:
    print("   Available Models for your Key:")
    found_any = False
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"   ✅ {m.name}")
            found_any = True
    
    if not found_any:
        print("   ❌ No text-generation models found for this key.")
        print("   Possible cause: Your API Key project might not have 'Generative Language API' enabled.")
    else:
        print("\n✨ Connection Successful! Update auditor.py with one of the names above.")

except Exception as e:
    print(f"\n❌ CONNECTION FAILED. Raw Error:\n{e}")