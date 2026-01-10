"""
Database connection module for Ruang Hijau Backend
Provides connection pool and helper functions for MySQL database
"""

import mysql.connector
from mysql.connector import pooling, Error
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', ''),
    'database': os.getenv('DB_NAME', 'ruang_hijau'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'use_pure': True,
    'autocommit': False,
    'raise_on_warnings': False,
}

# Create connection pool
try:
    connection_pool = pooling.MySQLConnectionPool(
        pool_name='ruang_hijau_pool',
        pool_size=5,
        pool_reset_session=True,
        **DB_CONFIG
    )
    print("✓ Database connection pool created successfully!")
except Error as err:
    print(f"✗ Error creating connection pool: {err}")
    connection_pool = None


def get_db():
    """
    Get a database connection from the pool
    Returns: MySQL connection object
    """
    try:
        if connection_pool:
            return connection_pool.get_connection()
        else:
            # Fallback to single connection if pool not available
            return mysql.connector.connect(**DB_CONFIG)
    except Error as err:
        print(f"✗ Error getting database connection: {err}")
        return None


def close_db(db):
    """
    Close database connection
    Args:
        db: MySQL connection object
    """
    try:
        if db and db.is_connected():
            db.close()
            print("✓ Database connection closed")
    except Error as err:
        print(f"✗ Error closing connection: {err}")


def test_connection():
    """
    Test database connection
    Returns: True if connection successful, False otherwise
    """
    db = None
    try:
        db = get_db()
        if db and db.is_connected():
            cursor = db.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            cursor.close()
            if result:
                print("✓ Database connection test successful!")
                return True
    except Error as err:
        print(f"✗ Database connection test failed: {err}")
        return False
    finally:
        if db:
            close_db(db)
    
    return False


def execute_query(query, params=None, fetch_one=False, fetch_all=True):
    """
    Execute a SELECT query
    Args:
        query (str): SQL SELECT query
        params (tuple): Query parameters for prepared statement
        fetch_one (bool): If True, return only one result
        fetch_all (bool): If True, return all results
    Returns:
        dict or list: Query result(s)
    """
    db = None
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        if fetch_one:
            result = cursor.fetchone()
        elif fetch_all:
            result = cursor.fetchall()
        else:
            result = None
        
        cursor.close()
        return result
    
    except Error as err:
        print(f"✗ Query execution error: {err}")
        return None
    finally:
        if db:
            close_db(db)


def execute_update(query, params=None):
    """
    Execute INSERT, UPDATE, or DELETE query
    Args:
        query (str): SQL INSERT/UPDATE/DELETE query
        params (tuple): Query parameters
    Returns:
        int: Last insert ID or affected rows count, -1 if error
    """
    db = None
    try:
        db = get_db()
        cursor = db.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        db.commit()
        
        result = cursor.lastrowid if 'INSERT' in query.upper() else cursor.rowcount
        cursor.close()
        
        return result
    
    except Error as err:
        if db:
            db.rollback()
        print(f"✗ Update execution error: {err}")
        return -1
    finally:
        if db:
            close_db(db)


def execute_many(query, data_list):
    """
    Execute multiple INSERT/UPDATE queries at once
    Args:
        query (str): SQL query with %s placeholders
        data_list (list): List of tuples with data
    Returns:
        int: Number of affected rows, -1 if error
    """
    db = None
    try:
        db = get_db()
        cursor = db.cursor()
        
        cursor.executemany(query, data_list)
        db.commit()
        
        result = cursor.rowcount
        cursor.close()
        
        return result
    
    except Error as err:
        if db:
            db.rollback()
        print(f"✗ Batch execution error: {err}")
        return -1
    finally:
        if db:
            close_db(db)


def call_procedure(procedure_name, args=None):
    """
    Call a stored procedure
    Args:
        procedure_name (str): Name of the stored procedure
        args (tuple): Arguments for the procedure
    Returns:
        list: Procedure results
    """
    db = None
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        if args:
            cursor.callproc(procedure_name, args)
        else:
            cursor.callproc(procedure_name)
        
        results = []
        for result in cursor.fetchall():
            results.append(result)
        
        db.commit()
        cursor.close()
        
        return results
    
    except Error as err:
        print(f"✗ Procedure call error: {err}")
        return []
    finally:
        if db:
            close_db(db)


# Convenience functions for common queries

def get_user_by_id(user_id):
    """Get user by ID"""
    query = "SELECT * FROM users WHERE id = %s"
    return execute_query(query, (user_id,), fetch_one=True)


def get_user_by_email(email):
    """Get user by email"""
    query = "SELECT * FROM users WHERE email = %s"
    return execute_query(query, (email,), fetch_one=True)


def get_campaign_by_id(campaign_id):
    """Get campaign by ID"""
    query = "SELECT * FROM campaigns WHERE id = %s"
    return execute_query(query, (campaign_id,), fetch_one=True)


def get_all_campaigns(status='active'):
    """Get all campaigns with optional status filter"""
    query = "SELECT * FROM campaigns WHERE campaign_status = %s ORDER BY created_at DESC"
    return execute_query(query, (status,))


def get_donations_by_campaign(campaign_id):
    """Get all donations for a campaign"""
    query = "SELECT * FROM donations WHERE campaign_id = %s ORDER BY created_at DESC"
    return execute_query(query, (campaign_id,))


def get_volunteers_by_campaign(campaign_id):
    """Get all volunteers for a campaign"""
    query = "SELECT v.*, u.name, u.email FROM volunteers v JOIN users u ON v.user_id = u.id WHERE v.campaign_id = %s ORDER BY v.created_at DESC"
    return execute_query(query, (campaign_id,))


def get_posts_by_user(user_id):
    """Get all posts by a user"""
    query = "SELECT * FROM posts WHERE user_id = %s ORDER BY created_at DESC"
    return execute_query(query, (user_id,))


def get_all_posts():
    """Get all posts"""
    query = "SELECT * FROM posts ORDER BY created_at DESC"
    return execute_query(query)


def create_user(name, email, password, phone=None, bio=None):
    """Create a new user"""
    query = "INSERT INTO users (name, email, password, phone, bio) VALUES (%s, %s, %s, %s, %s)"
    result = execute_update(query, (name, email, password, phone, bio))
    return result > 0


def create_campaign(title, description, target_amount, category, location, contact, creator_id, duration_days=None, need_volunteers=False):
    """Create a new campaign"""
    query = """
    INSERT INTO campaigns 
    (title, description, target_amount, category, location, contact, creator_id, duration_days, need_volunteers) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    params = (title, description, target_amount, category, location, contact, creator_id, duration_days, need_volunteers)
    result = execute_update(query, params)
    return result


def create_donation(campaign_id, amount, donor_id=None, donor_name=None, is_anonymous=False, payment_method='transfer_bank', transaction_id=None):
    """Create a new donation"""
    query = """
    INSERT INTO donations 
    (campaign_id, donor_id, amount, donor_name, is_anonymous, payment_method, transaction_id) 
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    params = (campaign_id, donor_id, amount, donor_name, is_anonymous, payment_method, transaction_id)
    result = execute_update(query, params)
    
    # Update campaign's current_amount
    if result > 0:
        update_campaign_amount(campaign_id, amount)
    
    return result


def update_campaign_amount(campaign_id, additional_amount):
    """Update campaign's current_amount"""
    query = "UPDATE campaigns SET current_amount = current_amount + %s WHERE id = %s"
    return execute_update(query, (additional_amount, campaign_id))


def add_post(user_id, text, image=None):
    """Add a new post"""
    query = "INSERT INTO posts (user_id, text, image) VALUES (%s, %s, %s)"
    return execute_update(query, (user_id, text, image))


def add_comment(post_id, user_id, text):
    """Add a comment to a post"""
    query = "INSERT INTO comments (post_id, user_id, text) VALUES (%s, %s, %s)"
    return execute_update(query, (post_id, user_id, text))


def add_like(post_id, user_id):
    """Add a like to a post"""
    query = "INSERT INTO likes (post_id, user_id) VALUES (%s, %s)"
    result = execute_update(query, (post_id, user_id))
    
    # Update post likes count
    if result > 0:
        execute_update("UPDATE posts SET likes = likes + 1 WHERE id = %s", (post_id,))
    
    return result > 0


def remove_like(post_id, user_id):
    """Remove a like from a post"""
    query = "DELETE FROM likes WHERE post_id = %s AND user_id = %s"
    result = execute_update(query, (post_id, user_id))
    
    # Update post likes count
    if result > 0:
        execute_update("UPDATE posts SET likes = likes - 1 WHERE id = %s", (post_id,))
    
    return result > 0


def create_volunteer(campaign_id, user_id):
    """Create a volunteer record"""
    query = "INSERT INTO volunteers (campaign_id, user_id) VALUES (%s, %s)"
    return execute_update(query, (campaign_id, user_id)) > 0


def update_volunteer_status(campaign_id, user_id, status):
    """Update volunteer status"""
    query = "UPDATE volunteers SET volunteer_status = %s WHERE campaign_id = %s AND user_id = %s"
    return execute_update(query, (status, campaign_id, user_id)) > 0


def create_notification(user_id, title, message, notification_type=None, related_id=None, related_type=None):
    """Create a notification"""
    query = """
    INSERT INTO notifications 
    (user_id, title, message, notification_type, related_id, related_type) 
    VALUES (%s, %s, %s, %s, %s, %s)
    """
    params = (user_id, title, message, notification_type, related_id, related_type)
    return execute_update(query, params) > 0


def get_user_notifications(user_id, unread_only=False):
    """Get user's notifications"""
    if unread_only:
        query = "SELECT * FROM notifications WHERE user_id = %s AND is_read = FALSE ORDER BY created_at DESC"
    else:
        query = "SELECT * FROM notifications WHERE user_id = %s ORDER BY created_at DESC"
    return execute_query(query, (user_id,))


def mark_notification_as_read(notification_id):
    """Mark notification as read"""
    query = "UPDATE notifications SET is_read = TRUE WHERE id = %s"
    return execute_update(query, (notification_id,)) > 0


if __name__ == "__main__":
    # Test database connection
    print("Testing database connection...")
    if test_connection():
        print("All systems operational!")
    else:
        print("Failed to connect to database. Please check your configuration.")
