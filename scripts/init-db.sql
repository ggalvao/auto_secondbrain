-- Initialize database for SecondBrain
-- This script is run when the PostgreSQL container starts

-- Create database if it doesn't exist
SELECT 'CREATE DATABASE secondbrain'
WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'secondbrain')\gexec

-- Connect to the secondbrain database
\c secondbrain

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE secondbrain TO postgres;
