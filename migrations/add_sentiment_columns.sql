-- ============================================================================
-- RUANG HIJAU APP - Feedback Sentiment Column Migration
-- Add sentiment analysis columns to feedback table
-- ============================================================================

USE ruang_hijau;

-- Add sentiment analysis columns to feedback table
ALTER TABLE feedback 
ADD COLUMN sentiment ENUM('positive', 'negative', 'neutral') DEFAULT NULL,
ADD COLUMN sentiment_score DECIMAL(5,3) DEFAULT NULL,
ADD COLUMN sentiment_confidence DECIMAL(5,3) DEFAULT NULL,
ADD COLUMN analyzed_at TIMESTAMP NULL DEFAULT NULL;

-- Add index for sentiment queries
CREATE INDEX idx_sentiment ON feedback(sentiment);
CREATE INDEX idx_sentiment_score ON feedback(sentiment_score);

-- ============================================================================
-- END OF MIGRATION
-- ============================================================================
