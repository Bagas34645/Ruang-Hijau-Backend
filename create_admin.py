#!/usr/bin/env python3
"""
Script to create admin user with hashed password
Run this after creating the database schema
"""

from werkzeug.security import generate_password_hash
from db import get_db
import sys

def create_admin():
    """Create admin user with hashed password"""
    try:
        db = get_db()
        cursor = db.cursor()
        
        # Admin credentials
        admin_email = 'admin@ruanghijau.com'
        admin_password = 'admin123'
        admin_name = 'Admin User'
        admin_phone = '081234567890'
        admin_bio = 'Administrator Ruang Hijau'
        
        # Hash password
        hashed_password = generate_password_hash(admin_password, method='pbkdf2:sha256')
        
        # Check if admin already exists
        cursor.execute("SELECT id FROM users WHERE email = %s", (admin_email,))
        existing = cursor.fetchone()
        
        if existing:
            # Update existing admin password
            cursor.execute("""
                UPDATE users 
                SET password = %s, name = %s, phone = %s, bio = %s, role = 'admin'
                WHERE email = %s
            """, (hashed_password, admin_name, admin_phone, admin_bio, admin_email))
            print(f"✅ Admin user updated: {admin_email}")
        else:
            # Create new admin user
            cursor.execute("""
                INSERT INTO users (name, email, password, phone, bio, role)
                VALUES (%s, %s, %s, %s, %s, 'admin')
            """, (admin_name, admin_email, hashed_password, admin_phone, admin_bio))
            print(f"✅ Admin user created: {admin_email}")
        
        db.commit()
        cursor.close()
        db.close()
        
        print("\n" + "="*50)
        print("Admin Login Credentials:")
        print("="*50)
        print(f"Email: {admin_email}")
        print(f"Password: {admin_password}")
        print("="*50)
        print("\n✅ Admin user ready! You can now login to admin panel.")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating admin: {str(e)}")
        if db:
            db.rollback()
            cursor.close()
            db.close()
        return False

if __name__ == "__main__":
    print("Creating admin user...")
    success = create_admin()
    sys.exit(0 if success else 1)
