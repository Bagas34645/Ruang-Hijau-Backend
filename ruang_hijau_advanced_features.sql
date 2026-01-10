-- ============================================================================
-- RUANG HIJAU APP - Advanced Features (Views & Stored Procedures)
-- ============================================================================
-- This file contains useful views and stored procedures for common operations

USE ruang_hijau;

-- ============================================================================
-- VIEWS
-- ============================================================================

-- ============================================================================
-- VIEW 1: Campaign Summary
-- ============================================================================
DROP VIEW IF EXISTS v_campaign_summary;
CREATE VIEW v_campaign_summary AS
SELECT 
    c.id,
    c.title,
    c.description,
    c.target_amount,
    c.current_amount,
    CONCAT(ROUND((c.current_amount / c.target_amount) * 100, 1), '%') AS progress_percentage,
    c.category,
    c.location,
    c.need_volunteers,
    c.campaign_status,
    u.name AS creator_name,
    u.email AS creator_email,
    COUNT(DISTINCT d.id) AS total_donations,
    COUNT(DISTINCT v.id) AS total_volunteers,
    c.created_at,
    c.updated_at
FROM campaigns c
JOIN users u ON c.creator_id = u.id
LEFT JOIN donations d ON c.id = d.campaign_id AND d.donation_status = 'completed'
LEFT JOIN volunteers v ON c.id = v.campaign_id
GROUP BY c.id, c.title, c.description, c.target_amount, c.current_amount, 
         c.category, c.location, c.need_volunteers, c.campaign_status, 
         u.name, u.email, c.created_at, c.updated_at;

-- ============================================================================
-- VIEW 2: Post Feed with Author Info
-- ============================================================================
DROP VIEW IF EXISTS v_post_feed;
CREATE VIEW v_post_feed AS
SELECT 
    p.id,
    p.user_id,
    u.name AS author_name,
    u.profile_photo AS author_photo,
    p.text,
    p.image,
    p.likes,
    COUNT(DISTINCT c.id) AS comment_count,
    COUNT(DISTINCT l.id) AS like_count,
    p.created_at,
    p.updated_at
FROM posts p
JOIN users u ON p.user_id = u.id
LEFT JOIN comments c ON p.id = c.post_id
LEFT JOIN likes l ON p.id = l.post_id
GROUP BY p.id, p.user_id, u.name, u.profile_photo, p.text, p.image, 
         p.likes, p.created_at, p.updated_at;

-- ============================================================================
-- VIEW 3: Event Details with Registrations
-- ============================================================================
DROP VIEW IF EXISTS v_event_details;
CREATE VIEW v_event_details AS
SELECT 
    e.id,
    e.title,
    e.description,
    e.date,
    e.location,
    e.image,
    e.event_status,
    u.name AS organizer_name,
    u.email AS organizer_email,
    u.phone AS organizer_phone,
    e.created_at,
    e.updated_at
FROM events e
LEFT JOIN users u ON e.organizer_id = u.id;

-- ============================================================================
-- VIEW 4: Donation Statistics
-- ============================================================================
DROP VIEW IF EXISTS v_donation_stats;
CREATE VIEW v_donation_stats AS
SELECT 
    d.campaign_id,
    c.title AS campaign_title,
    COUNT(d.id) AS total_donations,
    SUM(d.amount) AS total_amount,
    AVG(d.amount) AS average_donation,
    MIN(d.amount) AS min_donation,
    MAX(d.amount) AS max_donation,
    SUM(CASE WHEN d.is_anonymous = FALSE THEN 1 ELSE 0 END) AS identified_donors,
    SUM(CASE WHEN d.is_anonymous = TRUE THEN 1 ELSE 0 END) AS anonymous_donors
FROM donations d
JOIN campaigns c ON d.campaign_id = c.id
WHERE d.donation_status = 'completed'
GROUP BY d.campaign_id, c.title;

-- ============================================================================
-- VIEW 5: User Activity Summary
-- ============================================================================
DROP VIEW IF EXISTS v_user_activity;
CREATE VIEW v_user_activity AS
SELECT 
    u.id,
    u.name,
    u.email,
    COUNT(DISTINCT p.id) AS total_posts,
    COUNT(DISTINCT c.id) AS total_comments,
    COUNT(DISTINCT l.id) AS total_likes,
    COUNT(DISTINCT d.id) AS total_donations,
    COUNT(DISTINCT v.id) AS total_volunteer_applications,
    u.created_at,
    DATEDIFF(NOW(), u.created_at) AS days_member
FROM users u
LEFT JOIN posts p ON u.id = p.user_id
LEFT JOIN comments c ON u.id = c.user_id
LEFT JOIN likes l ON u.id = l.user_id
LEFT JOIN donations d ON u.id = d.donor_id
LEFT JOIN volunteers v ON u.id = v.user_id
GROUP BY u.id, u.name, u.email, u.created_at;

-- ============================================================================
-- VIEW 6: Top Donors
-- ============================================================================
DROP VIEW IF EXISTS v_top_donors;
CREATE VIEW v_top_donors AS
SELECT 
    d.donor_id,
    COALESCE(u.name, 'Anonymous') AS donor_name,
    COUNT(d.id) AS donation_count,
    SUM(d.amount) AS total_donation_amount,
    AVG(d.amount) AS average_donation,
    MAX(d.created_at) AS last_donation_date
FROM donations d
LEFT JOIN users u ON d.donor_id = u.id
WHERE d.donation_status = 'completed'
GROUP BY d.donor_id, u.name
ORDER BY total_donation_amount DESC;

-- ============================================================================
-- VIEW 7: Active Volunteers
-- ============================================================================
DROP VIEW IF EXISTS v_active_volunteers;
CREATE VIEW v_active_volunteers AS
SELECT 
    v.id,
    v.campaign_id,
    c.title AS campaign_title,
    v.user_id,
    u.name AS volunteer_name,
    u.email,
    u.phone,
    v.volunteer_status,
    v.hours_contributed,
    v.created_at,
    v.updated_at
FROM volunteers v
JOIN campaigns c ON v.campaign_id = c.id
JOIN users u ON v.user_id = u.id
WHERE v.volunteer_status IN ('accepted', 'completed');

-- ============================================================================
-- STORED PROCEDURES
-- ============================================================================

-- ============================================================================
-- PROCEDURE 1: Get Campaign Details with Statistics
-- ============================================================================
DROP PROCEDURE IF EXISTS sp_get_campaign_details;
DELIMITER //
CREATE PROCEDURE sp_get_campaign_details(IN p_campaign_id INT)
BEGIN
    SELECT 
        c.*,
        u.name AS creator_name,
        u.email AS creator_email,
        COUNT(DISTINCT d.id) AS total_donations,
        SUM(d.amount) AS total_raised,
        COUNT(DISTINCT v.id) AS active_volunteers,
        ROUND((c.current_amount / c.target_amount) * 100, 2) AS progress_percentage
    FROM campaigns c
    JOIN users u ON c.creator_id = u.id
    LEFT JOIN donations d ON c.id = d.campaign_id AND d.donation_status = 'completed'
    LEFT JOIN volunteers v ON c.id = v.campaign_id AND v.volunteer_status IN ('accepted', 'completed')
    WHERE c.id = p_campaign_id
    GROUP BY c.id;
END //
DELIMITER ;

-- ============================================================================
-- PROCEDURE 2: Record Donation and Update Campaign
-- ============================================================================
DROP PROCEDURE IF EXISTS sp_create_donation;
DELIMITER //
CREATE PROCEDURE sp_create_donation(
    IN p_campaign_id INT,
    IN p_donor_id INT,
    IN p_amount DECIMAL(15, 2),
    IN p_donor_name VARCHAR(100),
    IN p_is_anonymous BOOLEAN,
    IN p_payment_method VARCHAR(50),
    IN p_transaction_id VARCHAR(255)
)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SELECT 'ERROR' AS status, 'Failed to record donation' AS message;
    END;
    
    START TRANSACTION;
    
    -- Insert donation
    INSERT INTO donations 
    (campaign_id, donor_id, amount, donor_name, is_anonymous, payment_method, transaction_id, donation_status)
    VALUES (p_campaign_id, p_donor_id, p_amount, p_donor_name, p_is_anonymous, p_payment_method, p_transaction_id, 'completed');
    
    -- Update campaign amount
    UPDATE campaigns 
    SET current_amount = current_amount + p_amount 
    WHERE id = p_campaign_id;
    
    -- Create notification for campaign creator
    INSERT INTO notifications 
    (user_id, title, message, notification_type, related_id, related_type)
    SELECT 
        creator_id,
        'Donasi Diterima',
        CONCAT('Donasi sebesar Rp ', FORMAT(p_amount, 0), ' diterima untuk kampanye Anda'),
        'donation',
        p_campaign_id,
        'campaign'
    FROM campaigns WHERE id = p_campaign_id;
    
    COMMIT;
    SELECT 'SUCCESS' AS status, 'Donation recorded successfully' AS message;
END //
DELIMITER ;

-- ============================================================================
-- PROCEDURE 3: Get User Statistics
-- ============================================================================
DROP PROCEDURE IF EXISTS sp_get_user_stats;
DELIMITER //
CREATE PROCEDURE sp_get_user_stats(IN p_user_id INT)
BEGIN
    SELECT 
        u.id,
        u.name,
        u.email,
        (SELECT COUNT(*) FROM posts WHERE user_id = p_user_id) AS total_posts,
        (SELECT COUNT(*) FROM comments WHERE user_id = p_user_id) AS total_comments,
        (SELECT COUNT(*) FROM likes WHERE user_id = p_user_id) AS total_likes_given,
        (SELECT COUNT(*) FROM donations WHERE donor_id = p_user_id) AS total_donations_made,
        (SELECT SUM(amount) FROM donations WHERE donor_id = p_user_id AND donation_status = 'completed') AS total_donation_amount,
        (SELECT COUNT(*) FROM volunteers WHERE user_id = p_user_id) AS total_volunteer_applications,
        (SELECT COUNT(*) FROM volunteers WHERE user_id = p_user_id AND volunteer_status = 'completed') AS completed_volunteer_tasks,
        u.created_at
    FROM users u
    WHERE u.id = p_user_id;
END //
DELIMITER ;

-- ============================================================================
-- PROCEDURE 4: Get Campaign Leaderboard
-- ============================================================================
DROP PROCEDURE IF EXISTS sp_get_donation_leaderboard;
DELIMITER //
CREATE PROCEDURE sp_get_donation_leaderboard(IN p_campaign_id INT, IN p_limit INT)
BEGIN
    SELECT 
        @rank := @rank + 1 AS rank,
        CASE WHEN d.is_anonymous = TRUE THEN 'Anonymous' ELSE u.name END AS donor_name,
        d.amount AS donation_amount,
        d.created_at AS donation_date
    FROM donations d
    LEFT JOIN users u ON d.donor_id = u.id,
    (SELECT @rank := 0) r
    WHERE d.campaign_id = p_campaign_id AND d.donation_status = 'completed'
    ORDER BY d.amount DESC
    LIMIT p_limit;
END //
DELIMITER ;

-- ============================================================================
-- PROCEDURE 5: Search Campaigns
-- ============================================================================
DROP PROCEDURE IF EXISTS sp_search_campaigns;
DELIMITER //
CREATE PROCEDURE sp_search_campaigns(
    IN p_keyword VARCHAR(255),
    IN p_category VARCHAR(100),
    IN p_status VARCHAR(50)
)
BEGIN
    SELECT 
        c.*,
        u.name AS creator_name,
        COUNT(DISTINCT d.id) AS total_donations,
        SUM(d.amount) AS total_raised
    FROM campaigns c
    JOIN users u ON c.creator_id = u.id
    LEFT JOIN donations d ON c.id = d.campaign_id AND d.donation_status = 'completed'
    WHERE 
        (p_keyword IS NULL OR c.title LIKE CONCAT('%', p_keyword, '%') OR c.description LIKE CONCAT('%', p_keyword, '%'))
        AND (p_category IS NULL OR c.category = p_category)
        AND (p_status IS NULL OR c.campaign_status = p_status)
    GROUP BY c.id
    ORDER BY c.created_at DESC;
END //
DELIMITER ;

-- ============================================================================
-- PROCEDURE 6: Get User's Notification Feed
-- ============================================================================
DROP PROCEDURE IF EXISTS sp_get_notifications;
DELIMITER //
CREATE PROCEDURE sp_get_notifications(IN p_user_id INT, IN p_limit INT)
BEGIN
    SELECT * FROM notifications
    WHERE user_id = p_user_id
    ORDER BY created_at DESC
    LIMIT COALESCE(p_limit, 10);
END //
DELIMITER ;

-- ============================================================================
-- PROCEDURE 7: Accept Volunteer Application
-- ============================================================================
DROP PROCEDURE IF EXISTS sp_accept_volunteer;
DELIMITER //
CREATE PROCEDURE sp_accept_volunteer(
    IN p_campaign_id INT,
    IN p_user_id INT
)
BEGIN
    DECLARE v_campaign_title VARCHAR(200);
    
    START TRANSACTION;
    
    -- Update volunteer status
    UPDATE volunteers 
    SET volunteer_status = 'accepted'
    WHERE campaign_id = p_campaign_id AND user_id = p_user_id;
    
    -- Get campaign title
    SELECT title INTO v_campaign_title FROM campaigns WHERE id = p_campaign_id;
    
    -- Create notification for volunteer
    INSERT INTO notifications 
    (user_id, title, message, notification_type, related_id, related_type)
    VALUES (
        p_user_id,
        'Aplikasi Relawan Diterima',
        CONCAT('Selamat! Aplikasi Anda sebagai relawan untuk kampanye "', v_campaign_title, '" telah diterima.'),
        'volunteer',
        p_campaign_id,
        'campaign'
    );
    
    COMMIT;
    SELECT 'SUCCESS' AS status, 'Volunteer application accepted' AS message;
END //
DELIMITER ;

-- ============================================================================
-- PROCEDURE 8: Get Campaign Donation Timeline
-- ============================================================================
DROP PROCEDURE IF EXISTS sp_get_donation_timeline;
DELIMITER //
CREATE PROCEDURE sp_get_donation_timeline(IN p_campaign_id INT)
BEGIN
    SELECT 
        DATE(created_at) AS donation_date,
        COUNT(*) AS donation_count,
        SUM(amount) AS daily_total,
        SUM(SUM(amount)) OVER (ORDER BY DATE(created_at)) AS cumulative_total
    FROM donations
    WHERE campaign_id = p_campaign_id AND donation_status = 'completed'
    GROUP BY DATE(created_at)
    ORDER BY donation_date ASC;
END //
DELIMITER ;

-- ============================================================================
-- PROCEDURE 9: Get Popular Campaigns
-- ============================================================================
DROP PROCEDURE IF EXISTS sp_get_popular_campaigns;
DELIMITER //
CREATE PROCEDURE sp_get_popular_campaigns(IN p_limit INT)
BEGIN
    SELECT 
        c.*,
        u.name AS creator_name,
        COUNT(DISTINCT d.id) AS total_donations,
        SUM(d.amount) AS total_raised,
        COUNT(DISTINCT v.id) AS volunteer_count
    FROM campaigns c
    JOIN users u ON c.creator_id = u.id
    LEFT JOIN donations d ON c.id = d.campaign_id AND d.donation_status = 'completed'
    LEFT JOIN volunteers v ON c.id = v.campaign_id
    WHERE c.campaign_status = 'active'
    GROUP BY c.id
    ORDER BY total_raised DESC
    LIMIT COALESCE(p_limit, 10);
END //
DELIMITER ;

-- ============================================================================
-- PROCEDURE 10: Clean Up Old Notifications
-- ============================================================================
DROP PROCEDURE IF EXISTS sp_cleanup_old_notifications;
DELIMITER //
CREATE PROCEDURE sp_cleanup_old_notifications(IN p_days INT)
BEGIN
    DELETE FROM notifications
    WHERE created_at < DATE_SUB(NOW(), INTERVAL p_days DAY)
    AND is_read = TRUE;
    
    SELECT ROW_COUNT() AS deleted_count;
END //
DELIMITER ;

-- ============================================================================
-- INDEXES FOR PERFORMANCE OPTIMIZATION
-- ============================================================================

-- Optimize donation queries
CREATE INDEX idx_donations_campaign_status ON donations(campaign_id, donation_status);
CREATE INDEX idx_donations_donor_status ON donations(donor_id, donation_status);

-- Optimize volunteer queries
CREATE INDEX idx_volunteers_campaign_status ON volunteers(campaign_id, volunteer_status);
CREATE INDEX idx_volunteers_user_status ON volunteers(user_id, volunteer_status);

-- Optimize post queries
CREATE INDEX idx_posts_user_date ON posts(user_id, created_at);

-- Optimize notification queries
CREATE INDEX idx_notifications_user_read ON notifications(user_id, is_read);

-- Optimize comment queries
CREATE INDEX idx_comments_post_user ON comments(post_id, user_id);

-- ============================================================================
-- END OF ADVANCED FEATURES
-- ============================================================================
