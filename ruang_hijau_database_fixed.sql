-- ============================================================================
-- RUANG HIJAU APP - Complete Database Schema (FIXED VERSION)
-- MySQL Database Initialization Script
-- Fixed: Added google_id, password nullable, removed plain text passwords
-- ============================================================================

DROP DATABASE IF EXISTS ruang_hijau;
CREATE DATABASE ruang_hijau CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci;
USE ruang_hijau;

-- ============================================================================
-- TABLE: USERS
-- ============================================================================
DROP TABLE IF EXISTS users;
CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  email VARCHAR(150) NOT NULL UNIQUE,
  password VARCHAR(255) NULL,  -- NULLABLE untuk Google OAuth users
  google_id VARCHAR(255) NULL UNIQUE,  -- ADDED: Google OAuth support
  phone VARCHAR(20),
  profile_photo VARCHAR(255),
  bio TEXT,
  role ENUM('user', 'admin') DEFAULT 'user',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX idx_email (email),
  INDEX idx_google_id (google_id),  -- ADDED: Index for google_id
  INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- TABLE: POSTS
-- ============================================================================
DROP TABLE IF EXISTS posts;
CREATE TABLE posts (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  text TEXT,
  image VARCHAR(255),
  likes INT DEFAULT 0,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  INDEX idx_user_id (user_id),
  INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- TABLE: COMMENTS
-- ============================================================================
DROP TABLE IF EXISTS comments;
CREATE TABLE comments (
  id INT AUTO_INCREMENT PRIMARY KEY,
  post_id INT NOT NULL,
  user_id INT NOT NULL,
  text TEXT NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  INDEX idx_post_id (post_id),
  INDEX idx_user_id (user_id),
  INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- TABLE: CAMPAIGNS
-- ============================================================================
DROP TABLE IF EXISTS campaigns;
CREATE TABLE campaigns (
  id INT AUTO_INCREMENT PRIMARY KEY,
  title VARCHAR(200) NOT NULL,
  description TEXT NOT NULL,
  target_amount DECIMAL(15, 2) NOT NULL,
  current_amount DECIMAL(15, 2) DEFAULT 0,
  category VARCHAR(100),
  image VARCHAR(255),
  location VARCHAR(255),
  contact VARCHAR(100),
  duration_days INT,
  need_volunteers BOOLEAN DEFAULT FALSE,
  campaign_status ENUM('active', 'completed', 'cancelled') DEFAULT 'active',
  creator_id INT NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (creator_id) REFERENCES users(id) ON DELETE CASCADE,
  INDEX idx_creator_id (creator_id),
  INDEX idx_category (category),
  INDEX idx_status (campaign_status),
  INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- TABLE: DONATIONS
-- ============================================================================
DROP TABLE IF EXISTS donations;
CREATE TABLE donations (
  id INT AUTO_INCREMENT PRIMARY KEY,
  campaign_id INT NOT NULL,
  donor_id INT,  -- FIXED: Using donor_id (not user_id)
  amount DECIMAL(15, 2) NOT NULL,
  donor_name VARCHAR(100),
  is_anonymous BOOLEAN DEFAULT FALSE,
  payment_method VARCHAR(50),
  transaction_id VARCHAR(255) UNIQUE,
  donation_status ENUM('pending', 'completed', 'failed', 'refunded') DEFAULT 'completed',  -- FIXED: donation_status (not status)
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE,
  FOREIGN KEY (donor_id) REFERENCES users(id) ON DELETE SET NULL,
  INDEX idx_campaign_id (campaign_id),
  INDEX idx_donor_id (donor_id),
  INDEX idx_status (donation_status),
  INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- TABLE: VOLUNTEERS
-- ============================================================================
DROP TABLE IF EXISTS volunteers;
CREATE TABLE volunteers (
  id INT AUTO_INCREMENT PRIMARY KEY,
  campaign_id INT NOT NULL,
  user_id INT NOT NULL,
  volunteer_status ENUM('applied', 'accepted', 'rejected', 'completed') DEFAULT 'applied',  -- FIXED: volunteer_status (not status)
  hours_contributed DECIMAL(5, 2) DEFAULT 0,
  notes TEXT,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  UNIQUE KEY unique_volunteer (campaign_id, user_id),
  FOREIGN KEY (campaign_id) REFERENCES campaigns(id) ON DELETE CASCADE,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  INDEX idx_campaign_id (campaign_id),
  INDEX idx_user_id (user_id),
  INDEX idx_status (volunteer_status),
  INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- TABLE: NOTIFICATIONS
-- ============================================================================
DROP TABLE IF EXISTS notifications;
CREATE TABLE notifications (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  title VARCHAR(200) NOT NULL,
  message TEXT,
  notification_type VARCHAR(50),
  is_read BOOLEAN DEFAULT FALSE,
  related_id INT,
  related_type VARCHAR(50),
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  INDEX idx_user_id (user_id),
  INDEX idx_is_read (is_read),
  INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- TABLE: LIKES
-- ============================================================================
DROP TABLE IF EXISTS likes;
CREATE TABLE likes (
  id INT AUTO_INCREMENT PRIMARY KEY,
  post_id INT NOT NULL,
  user_id INT NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY unique_like (post_id, user_id),
  FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  INDEX idx_post_id (post_id),
  INDEX idx_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- SAMPLE DATA (WITHOUT PASSWORDS - Use create_admin.py to create admin)
-- ============================================================================

-- Sample Users (without passwords - passwords must be hashed using create_admin.py)
-- NOTE: Run create_admin.py script to create admin user with hashed password
-- INSERT INTO users (name, email, phone, bio, role) VALUES
-- ('Bagas Pratama', 'bagas@example.com', '081234567891', 'Pencinta lingkungan dan relawan sosial', 'user'),
-- ('Siti Nurhaliza', 'siti@example.com', '081234567892', 'Aktivis keberlanjutan lingkungan', 'user'),
-- ('Budi Santoso', 'budi@example.com', '081234567893', 'Relawan pendidikan', 'user'),
-- ('Maya Wijaya', 'maya@example.com', '081234567894', 'Pendonor tetap', 'user');

-- Sample Campaigns
-- INSERT INTO campaigns (title, description, target_amount, category, location, contact, duration_days, need_volunteers, creator_id) VALUES
-- ('Penanaman Pohon di Taman Kota', 'Proyek penanaman 1000 pohon untuk memperbaiki udara di kawasan perkotaan', 50000000, 'Lingkungan', 'Jakarta, Indonesia', '081234567890', 90, TRUE, 1),
-- ('Beasiswa untuk Anak Kurang Mampu', 'Kumpulkan dana untuk memberikan beasiswa kepada 50 anak kurang mampu', 200000000, 'Pendidikan', 'Bandung, Indonesia', '082345678901', 180, TRUE, 2),
-- ('Program Vaksinasi Gratis', 'Vaksinasi gratis untuk masyarakat yang tidak mampu', 150000000, 'Kesehatan', 'Surabaya, Indonesia', '083456789012', 60, TRUE, 1),
-- ('Pembersihan Pantai', 'Bersihkan pantai dari sampah plastik dan limbah', 30000000, 'Lingkungan', 'Bali, Indonesia', '084567890123', 30, TRUE, 3),
-- ('Perpustakaan Digital untuk Desa', 'Bangun perpustakaan digital di daerah terpencil', 100000000, 'Pendidikan', 'Yogyakarta, Indonesia', '085678901234', 120, FALSE, 2);

-- Sample Donations
-- INSERT INTO donations (campaign_id, donor_id, amount, is_anonymous, payment_method, donation_status) VALUES
-- (1, 1, 5000000, FALSE, 'transfer_bank', 'completed'),
-- (1, 4, 2500000, FALSE, 'e_wallet', 'completed'),
-- (1, NULL, 1000000, TRUE, 'transfer_bank', 'completed'),
-- (2, 2, 10000000, FALSE, 'transfer_bank', 'completed'),
-- (2, 3, 7500000, FALSE, 'qris', 'completed'),
-- (3, 1, 15000000, FALSE, 'transfer_bank', 'completed'),
-- (4, 4, 3000000, FALSE, 'e_wallet', 'completed'),
-- (5, 2, 5000000, FALSE, 'transfer_bank', 'completed');

-- Sample Volunteers
-- INSERT INTO volunteers (campaign_id, user_id, volunteer_status) VALUES
-- (1, 2, 'accepted'),
-- (1, 3, 'applied'),
-- (2, 1, 'accepted'),
-- (3, 3, 'accepted'),
-- (4, 4, 'completed'),
-- (4, 1, 'accepted'),
-- (5, 2, 'applied');

-- Sample Posts
-- INSERT INTO posts (user_id, text, likes) VALUES
-- (1, 'Hari ini kami mulai penanaman pohon pertama di proyek "Penanaman Pohon di Taman Kota"! 🌱', 25),
-- (2, 'Terima kasih kepada semua yang telah berdonasi untuk "Beasiswa untuk Anak Kurang Mampu". Semoga berkah! ❤️', 18),
-- (3, 'Bergabunglah dengan kami untuk membersihkan pantai minggu depan!', 12),
-- (4, 'Sudah saatnya kita peduli lingkungan. Mari bersama-sama membuat perbedaan! 🌍', 34);

-- Sample Comments
-- INSERT INTO comments (post_id, user_id, text) VALUES
-- (1, 2, 'Bagus sekali inisiatifnya! Saya ingin turut serta.'),
-- (1, 3, 'Kapan bisa bergabung? Saya tertarik.'),
-- (2, 1, 'Luar biasa! Semoga banyak anak yang terbantu.'),
-- (4, 2, 'Saya setuju! Mari kita jaga bumi ini bersama-sama.');

-- Sample Notifications
-- INSERT INTO notifications (user_id, title, message, notification_type, related_id, related_type) VALUES
-- (1, 'Donasi Diterima', 'Terima kasih! Donasi Anda sebesar Rp 5.000.000 telah diterima untuk kampanye "Penanaman Pohon"', 'donation', 1, 'campaign'),
-- (2, 'Volunteer Diterima', 'Selamat! Aplikasi Anda sebagai relawan untuk kampanye "Beasiswa untuk Anak Kurang Mampu" telah diterima.', 'volunteer', 2, 'campaign'),
-- (3, 'Komentar Baru', 'Bagas Pratama mengomentari postingan Anda', 'comment', 1, 'post');

-- Sample Likes
-- INSERT INTO likes (post_id, user_id) VALUES
-- (1, 1), (1, 2), (1, 3), (1, 4),
-- (2, 1), (2, 3), (2, 4),
-- (3, 1), (3, 3),
-- (4, 1), (4, 2), (4, 3), (4, 4);

-- ============================================================================
-- TABLE: FEEDBACK
-- ============================================================================
DROP TABLE IF EXISTS feedback;
CREATE TABLE feedback (
  id INT AUTO_INCREMENT PRIMARY KEY,
  user_id INT NOT NULL,
  category VARCHAR(50) NOT NULL,
  rating INT NOT NULL CHECK (rating >= 1 AND rating <= 5),
  message TEXT NOT NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  INDEX idx_user_id (user_id),
  INDEX idx_category (category),
  INDEX idx_rating (rating),
  INDEX idx_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ============================================================================
-- CREATE INDEXES FOR PERFORMANCE
-- ============================================================================

-- Additional indexes for common queries
CREATE INDEX idx_campaigns_current_amount ON campaigns(current_amount);
CREATE INDEX idx_donations_amount ON donations(amount);
CREATE INDEX idx_volunteers_hours ON volunteers(hours_contributed);
CREATE INDEX idx_notifications_related ON notifications(related_id, related_type);

-- ============================================================================
-- END OF DATABASE SCHEMA
-- ============================================================================
-- 
-- IMPORTANT: After running this script, run create_admin.py to create admin user
-- with properly hashed password:
--   python create_admin.py
-- 
-- This will create admin user with:
--   Email: admin@ruanghijau.com
--   Password: admin123
-- ============================================================================
