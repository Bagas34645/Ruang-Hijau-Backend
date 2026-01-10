-- ============================================================================
-- RUANG HIJAU APP - Testing & Development Queries
-- ============================================================================
-- Useful queries for development, testing, and maintenance

USE ruang_hijau;

-- ============================================================================
-- SECTION 1: DATA INSPECTION & VERIFICATION
-- ============================================================================

-- Check database size
SELECT 
    ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS 'Database Size (MB)'
FROM information_schema.TABLES 
WHERE table_schema = 'ruang_hijau';

-- Check table sizes
SELECT 
    TABLE_NAME,
    ROUND(((data_length + index_length) / 1024 / 1024), 2) AS 'Size (MB)'
FROM information_schema.TABLES 
WHERE TABLE_SCHEMA = 'ruang_hijau'
ORDER BY (data_length + index_length) DESC;

-- Count records in each table
SELECT 
    'users' AS table_name, COUNT(*) AS count FROM users UNION ALL
SELECT 'posts', COUNT(*) FROM posts UNION ALL
SELECT 'comments', COUNT(*) FROM comments UNION ALL
SELECT 'events', COUNT(*) FROM events UNION ALL
SELECT 'campaigns', COUNT(*) FROM campaigns UNION ALL
SELECT 'donations', COUNT(*) FROM donations UNION ALL
SELECT 'volunteers', COUNT(*) FROM volunteers UNION ALL
SELECT 'notifications', COUNT(*) FROM notifications UNION ALL
SELECT 'likes', COUNT(*) FROM likes;

-- ============================================================================
-- SECTION 2: USER MANAGEMENT QUERIES
-- ============================================================================

-- List all users with role
SELECT id, name, email, role, created_at FROM users ORDER BY created_at DESC;

-- Find duplicate emails (data validation)
SELECT email, COUNT(*) AS count 
FROM users 
GROUP BY email 
HAVING count > 1;

-- Get user activity summary
SELECT 
    u.id,
    u.name,
    u.email,
    (SELECT COUNT(*) FROM posts WHERE user_id = u.id) AS posts_count,
    (SELECT COUNT(*) FROM comments WHERE user_id = u.id) AS comments_count,
    (SELECT COUNT(*) FROM donations WHERE donor_id = u.id) AS donations_count,
    (SELECT COUNT(*) FROM volunteers WHERE user_id = u.id) AS volunteer_count,
    u.created_at
FROM users u
ORDER BY u.created_at DESC;

-- Get users without any activity
SELECT u.* 
FROM users u
WHERE u.id NOT IN (SELECT DISTINCT user_id FROM posts)
AND u.id NOT IN (SELECT DISTINCT user_id FROM comments)
AND u.id NOT IN (SELECT DISTINCT donor_id FROM donations)
AND u.id NOT IN (SELECT DISTINCT user_id FROM volunteers);

-- ============================================================================
-- SECTION 3: CAMPAIGN QUERIES
-- ============================================================================

-- Get campaign progress
SELECT 
    id,
    title,
    target_amount,
    current_amount,
    CONCAT(ROUND((current_amount / target_amount) * 100, 1), '%') AS progress,
    campaign_status,
    created_at
FROM campaigns
ORDER BY created_at DESC;

-- Get campaigns by category
SELECT 
    category,
    COUNT(*) AS campaign_count,
    SUM(current_amount) AS total_raised,
    AVG(current_amount) AS avg_raised
FROM campaigns
WHERE campaign_status = 'active'
GROUP BY category;

-- Get campaigns that reached target
SELECT 
    id,
    title,
    target_amount,
    current_amount,
    (current_amount - target_amount) AS exceeded_amount,
    DATEDIFF(NOW(), created_at) AS days_active
FROM campaigns
WHERE current_amount >= target_amount
ORDER BY exceeded_amount DESC;

-- Get campaigns that need attention (low progress)
SELECT 
    id,
    title,
    target_amount,
    current_amount,
    ROUND((current_amount / target_amount) * 100, 1) AS progress_percent,
    duration_days,
    DATEDIFF(DATE_ADD(created_at, INTERVAL duration_days DAY), NOW()) AS days_remaining
FROM campaigns
WHERE campaign_status = 'active'
AND (current_amount / target_amount) < 0.5
ORDER BY created_at ASC;

-- ============================================================================
-- SECTION 4: DONATION QUERIES
-- ============================================================================

-- Donation summary by campaign
SELECT 
    c.id,
    c.title,
    COUNT(d.id) AS total_donations,
    SUM(d.amount) AS total_amount,
    AVG(d.amount) AS avg_amount,
    MIN(d.amount) AS min_amount,
    MAX(d.amount) AS max_amount,
    SUM(CASE WHEN d.is_anonymous = FALSE THEN 1 ELSE 0 END) AS identified_donors,
    SUM(CASE WHEN d.is_anonymous = TRUE THEN 1 ELSE 0 END) AS anonymous_donors
FROM campaigns c
LEFT JOIN donations d ON c.id = d.campaign_id AND d.donation_status = 'completed'
GROUP BY c.id, c.title
ORDER BY total_amount DESC;

-- Get top donors overall
SELECT 
    COALESCE(u.name, 'Anonymous') AS donor_name,
    COUNT(d.id) AS donation_count,
    SUM(d.amount) AS total_amount,
    AVG(d.amount) AS avg_donation,
    MAX(d.created_at) AS last_donation
FROM donations d
LEFT JOIN users u ON d.donor_id = u.id
WHERE d.donation_status = 'completed'
GROUP BY d.donor_id
ORDER BY total_amount DESC
LIMIT 20;

-- Get failed/pending donations
SELECT 
    d.id,
    c.title,
    d.amount,
    d.donation_status,
    d.created_at,
    DATEDIFF(NOW(), d.created_at) AS days_ago
FROM donations d
JOIN campaigns c ON d.campaign_id = c.id
WHERE d.donation_status IN ('pending', 'failed')
ORDER BY d.created_at ASC;

-- Donation trend (daily)
SELECT 
    DATE(created_at) AS donation_date,
    COUNT(*) AS count,
    SUM(amount) AS daily_total,
    ROUND(AVG(amount), 2) AS avg_donation
FROM donations
WHERE donation_status = 'completed'
GROUP BY DATE(created_at)
ORDER BY donation_date DESC
LIMIT 30;

-- ============================================================================
-- SECTION 5: VOLUNTEER QUERIES
-- ============================================================================

-- Volunteer summary by campaign
SELECT 
    c.id,
    c.title,
    COUNT(DISTINCT CASE WHEN v.volunteer_status = 'applied' THEN v.id END) AS applied,
    COUNT(DISTINCT CASE WHEN v.volunteer_status = 'accepted' THEN v.id END) AS accepted,
    COUNT(DISTINCT CASE WHEN v.volunteer_status = 'rejected' THEN v.id END) AS rejected,
    COUNT(DISTINCT CASE WHEN v.volunteer_status = 'completed' THEN v.id END) AS completed,
    SUM(CASE WHEN v.volunteer_status = 'completed' THEN v.hours_contributed ELSE 0 END) AS total_hours
FROM campaigns c
LEFT JOIN volunteers v ON c.id = v.campaign_id
GROUP BY c.id, c.title;

-- Get most active volunteers
SELECT 
    u.id,
    u.name,
    u.email,
    COUNT(v.id) AS volunteer_count,
    SUM(v.hours_contributed) AS total_hours,
    COUNT(DISTINCT CASE WHEN v.volunteer_status = 'completed' THEN v.id END) AS completed_tasks
FROM users u
JOIN volunteers v ON u.id = v.user_id
GROUP BY u.id, u.name, u.email
ORDER BY total_hours DESC;

-- Get volunteer applications pending approval
SELECT 
    v.id,
    v.campaign_id,
    c.title AS campaign_title,
    u.name AS volunteer_name,
    u.email,
    v.created_at
FROM volunteers v
JOIN campaigns c ON v.campaign_id = c.id
JOIN users u ON v.user_id = u.id
WHERE v.volunteer_status = 'applied'
ORDER BY v.created_at ASC;

-- ============================================================================
-- SECTION 6: POST & COMMENT QUERIES
-- ============================================================================

-- Most liked posts
SELECT 
    p.id,
    u.name AS author,
    p.text,
    p.likes,
    COUNT(c.id) AS comment_count,
    p.created_at
FROM posts p
JOIN users u ON p.user_id = u.id
LEFT JOIN comments c ON p.id = c.post_id
GROUP BY p.id, u.name, p.text, p.likes, p.created_at
ORDER BY p.likes DESC
LIMIT 20;

-- Most commented posts
SELECT 
    p.id,
    u.name AS author,
    p.text,
    p.likes,
    COUNT(c.id) AS comment_count,
    p.created_at
FROM posts p
JOIN users u ON p.user_id = u.id
LEFT JOIN comments c ON p.id = c.post_id
GROUP BY p.id, u.name, p.text, p.likes, p.created_at
ORDER BY comment_count DESC
LIMIT 20;

-- Users with most posts
SELECT 
    u.id,
    u.name,
    u.email,
    COUNT(p.id) AS post_count,
    SUM(p.likes) AS total_likes,
    AVG(p.likes) AS avg_likes_per_post
FROM users u
LEFT JOIN posts p ON u.id = p.user_id
GROUP BY u.id, u.name, u.email
ORDER BY post_count DESC
LIMIT 20;

-- Engagement metrics
SELECT 
    u.name,
    COUNT(DISTINCT p.id) AS posts,
    SUM(p.likes) AS total_likes,
    COUNT(DISTINCT c.id) AS comments_made,
    COUNT(DISTINCT l.id) AS likes_given
FROM users u
LEFT JOIN posts p ON u.id = p.user_id
LEFT JOIN comments c ON u.id = c.user_id
LEFT JOIN likes l ON u.id = l.user_id
GROUP BY u.name
ORDER BY total_likes DESC;

-- ============================================================================
-- SECTION 7: NOTIFICATION QUERIES
-- ============================================================================

-- Count unread notifications per user
SELECT 
    u.name,
    COUNT(n.id) AS unread_count,
    MAX(n.created_at) AS latest_notification
FROM users u
LEFT JOIN notifications n ON u.id = n.user_id AND n.is_read = FALSE
GROUP BY u.name
HAVING unread_count > 0
ORDER BY unread_count DESC;

-- Notification distribution by type
SELECT 
    notification_type,
    COUNT(*) AS count,
    SUM(CASE WHEN is_read = FALSE THEN 1 ELSE 0 END) AS unread
FROM notifications
GROUP BY notification_type;

-- Get old unread notifications (might be stale)
SELECT 
    n.id,
    u.name,
    n.title,
    n.created_at,
    DATEDIFF(NOW(), n.created_at) AS days_ago
FROM notifications n
JOIN users u ON n.user_id = u.id
WHERE n.is_read = FALSE
AND n.created_at < DATE_SUB(NOW(), INTERVAL 30 DAY)
ORDER BY n.created_at ASC;

-- ============================================================================
-- SECTION 8: DATA CLEANUP & MAINTENANCE
-- ============================================================================

-- Find orphaned records (optional - use with caution)
-- Comments with non-existent posts
SELECT c.* FROM comments c
WHERE c.post_id NOT IN (SELECT id FROM posts);

-- Donations with non-existent campaigns
SELECT d.* FROM donations d
WHERE d.campaign_id NOT IN (SELECT id FROM campaigns);

-- Volunteers with non-existent campaigns
SELECT v.* FROM volunteers v
WHERE v.campaign_id NOT IN (SELECT id FROM campaigns);

-- Delete old unread notifications (30+ days old)
-- DELETE FROM notifications
-- WHERE is_read = FALSE 
-- AND created_at < DATE_SUB(NOW(), INTERVAL 30 DAY);

-- Reset auto-increment for a table
-- ALTER TABLE users AUTO_INCREMENT = 1;

-- ============================================================================
-- SECTION 9: TESTING DATA GENERATION
-- ============================================================================

-- Add test user
INSERT INTO users (name, email, password, phone, bio, role) VALUES
('Test User', 'test_user_' + UNIX_TIMESTAMP() + '@test.com', 'password123', '081234567890', 'Test user', 'user');

-- Add test campaign
INSERT INTO campaigns (title, description, target_amount, category, location, contact, creator_id, duration_days, need_volunteers, campaign_status)
VALUES ('Test Campaign', 'This is a test campaign', 50000000, 'Lingkungan', 'Jakarta', '081234567890', 1, 90, TRUE, 'active');

-- Add test donation
INSERT INTO donations (campaign_id, donor_id, amount, is_anonymous, payment_method, donation_status)
VALUES (1, 2, 5000000, FALSE, 'transfer_bank', 'completed');

-- ============================================================================
-- SECTION 10: PERFORMANCE ANALYSIS
-- ============================================================================

-- Check index usage
SELECT 
    object_schema,
    object_name,
    index_name,
    count_read,
    count_write,
    count_delete,
    count_update,
    count_insert
FROM performance_schema.table_io_waits_summary_by_index_usage
WHERE object_schema = 'ruang_hijau'
ORDER BY count_read DESC;

-- Find slow queries (requires slow query log enabled)
-- SELECT * FROM mysql.slow_log;

-- Check table fragmentation
SELECT 
    TABLE_NAME,
    ROUND(data_free / 1024 / 1024, 2) AS 'Fragmentation (MB)'
FROM information_schema.TABLES
WHERE TABLE_SCHEMA = 'ruang_hijau'
AND data_free > 0
ORDER BY data_free DESC;

-- ============================================================================
-- SECTION 11: EXPORT/IMPORT QUERIES
-- ============================================================================

-- Export campaigns to CSV (MySQL command line)
-- SELECT * FROM campaigns INTO OUTFILE '/tmp/campaigns.csv' FIELDS TERMINATED BY ',' ENCLOSED BY '"';

-- Export user data (anonymized)
SELECT 
    id,
    'user_' + CAST(id AS CHAR) AS anonymized_name,
    'user_' + CAST(id AS CHAR) + '@example.com' AS anonymized_email,
    role,
    created_at
FROM users;

-- ============================================================================
-- SECTION 12: REPORTING QUERIES
-- ============================================================================

-- Monthly report
SELECT 
    YEAR(created_at) AS year,
    MONTH(created_at) AS month,
    COUNT(DISTINCT CASE WHEN 'users' THEN id END) AS new_users,
    COUNT(DISTINCT CASE WHEN 'donations' THEN id END) AS donations,
    SUM(CASE WHEN 'donations' THEN amount ELSE 0 END) AS total_amount
FROM (
    SELECT id, created_at FROM users
    UNION ALL
    SELECT id, created_at FROM donations
) AS combined
GROUP BY YEAR(created_at), MONTH(created_at)
ORDER BY year DESC, month DESC;

-- Top campaigns this month
SELECT 
    c.id,
    c.title,
    COUNT(d.id) AS month_donations,
    SUM(d.amount) AS month_raised,
    c.current_amount AS total_raised
FROM campaigns c
LEFT JOIN donations d ON c.id = d.campaign_id 
    AND MONTH(d.created_at) = MONTH(NOW())
    AND YEAR(d.created_at) = YEAR(NOW())
GROUP BY c.id
ORDER BY month_raised DESC;

-- ============================================================================
-- END OF TESTING & DEVELOPMENT QUERIES
-- ============================================================================
