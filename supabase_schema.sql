-- JobSniper Jobs Table Schema for Supabase
-- Run this in Supabase SQL Editor to create the jobs table

CREATE TABLE IF NOT EXISTS jobs (
    id BIGSERIAL PRIMARY KEY,
    company TEXT NOT NULL,
    role TEXT NOT NULL,
    location TEXT,
    duration TEXT,
    link TEXT UNIQUE NOT NULL,
    match_score REAL,
    status TEXT DEFAULT 'Not Applied',
    notes TEXT,
    date_found TEXT,
    date_applied TEXT,
    date_updated TEXT,
    CONSTRAINT valid_status CHECK (status IN ('Not Applied', 'Applied', 'Ongoing', 'Interviewing', 'Got Selected', 'Rejected'))
);

-- Enable Row Level Security (RLS)
ALTER TABLE jobs ENABLE ROW LEVEL SECURITY;

-- Create policy to allow all operations
-- Note: This allows public access. You can customize this later for better security.
CREATE POLICY "Enable all access for authenticated users" ON jobs
    FOR ALL
    USING (true)
    WITH CHECK (true);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);
CREATE INDEX IF NOT EXISTS idx_jobs_date_found ON jobs(date_found DESC);
CREATE INDEX IF NOT EXISTS idx_jobs_match_score ON jobs(match_score DESC);
CREATE INDEX IF NOT EXISTS idx_jobs_link ON jobs(link);
