-- PostgreSQL initialization script for Terminal Academy
-- This runs when the container is first created

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Set timezone
SET timezone = 'UTC';

-- Create indexes for common queries (these will be created by Django migrations too)
-- This is just documentation of important indexes

-- Performance tips:
-- 1. Run ANALYZE periodically: ANALYZE;
-- 2. Check for slow queries: SELECT * FROM pg_stat_activity WHERE state = 'active';
-- 3. Check table sizes: SELECT relname, pg_size_pretty(pg_total_relation_size(relid)) FROM pg_catalog.pg_statio_user_tables ORDER BY pg_total_relation_size(relid) DESC;
