# Supabase Setup Guide

## Step 1: Create Supabase Account
1. Go to https://supabase.com
2. Click "Start your project" or "Sign in"
3. Sign up with GitHub (recommended) or email

## Step 2: Create New Project
1. Once logged in, click "New Project"
2. Fill in the details:
   - **Name**: JobSniper (or any name you prefer)
   - **Database Password**: Create a strong password (save this!)
   - **Region**: Choose closest to you (e.g., Mumbai for India)
   - **Pricing Plan**: Free tier is perfect
3. Click "Create new project"
4. Wait 1-2 minutes for project to be provisioned

## Step 3: Get Your Credentials
1. Once project is ready, go to **Project Settings** (gear icon in sidebar)
2. Click on **API** in the left menu
3. You'll see:
   - **Project URL**: Something like `https://xxxxxxxxxxxxx.supabase.co`
   - **Project API keys**:
     - Find the **anon** **public** key (long string starting with `eyJ...`)

## Step 4: Copy These Values
Copy these two values:
```
SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6I...
```

## Step 5: Provide to Me
Once you have these values, add them to your `.env` file or provide them to me, and I'll complete the migration!

---

**Note**: The migration script will automatically:
- Create the `jobs` table in Supabase
- Migrate all 38 existing jobs
- Verify data integrity
- Keep a backup of your SQLite database
