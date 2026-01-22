-- ============================================================================
-- Migration: Add Google OAuth Support
-- Date: 2026-01-22
-- Description: Adds google_id column to users table for Google Sign-In support
-- ============================================================================

-- Add google_id column to users table
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS google_id VARCHAR(255) NULL UNIQUE AFTER password;

-- Add index for google_id for faster lookups
CREATE INDEX IF NOT EXISTS idx_google_id ON users(google_id);

-- Make password nullable for Google-only users
ALTER TABLE users 
MODIFY COLUMN password VARCHAR(255) NULL;

-- ============================================================================
-- ROLLBACK (if needed):
-- ALTER TABLE users DROP COLUMN google_id;
-- ALTER TABLE users MODIFY COLUMN password VARCHAR(255) NOT NULL;
-- ============================================================================
