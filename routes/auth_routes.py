from flask import Blueprint, request, jsonify
from db import get_db
from werkzeug.security import generate_password_hash, check_password_hash
import re

auth_bp = Blueprint("auth", __name__)


def is_valid_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


# REGISTER
@auth_bp.route("/register", methods=["POST"])
def register():
    """
    Register a new user
    Expected JSON: {
        "name": "User Name",
        "email": "user@example.com",
        "password": "password123",
        "phone": "081234567890" (optional),
        "bio": "User bio" (optional)
    }
    
    Response: 201 Created
    {
        "status": "success",
        "message": "Registration successful",
        "user": {
            "id": 1,
            "name": "User Name",
            "email": "user@example.com",
            "phone": "081234567890",
            "bio": "User bio",
            "profile_photo": null
        }
    }
    """
    try:
        data = request.json
        
        # Validate request data exists
        if not data:
            return jsonify({
                "status": "error",
                "message": "Request body cannot be empty"
            }), 400
        
        # Validate required fields
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        phone = data.get('phone', '').strip() if data.get('phone') else None
        bio = data.get('bio', '').strip() if data.get('bio') else None
        
        # Validation: Name
        if not name:
            return jsonify({
                "status": "error",
                "message": "Name is required"
            }), 400
        
        if len(name) < 3:
            return jsonify({
                "status": "error",
                "message": "Name must be at least 3 characters"
            }), 400
        
        if len(name) > 100:
            return jsonify({
                "status": "error",
                "message": "Name cannot exceed 100 characters"
            }), 400
        
        # Validation: Email
        if not email:
            return jsonify({
                "status": "error",
                "message": "Email is required"
            }), 400
        
        if not is_valid_email(email):
            return jsonify({
                "status": "error",
                "message": "Email format is invalid"
            }), 400
        
        # Validation: Password
        if not password:
            return jsonify({
                "status": "error",
                "message": "Password is required"
            }), 400
        
        if len(password) < 6:
            return jsonify({
                "status": "error",
                "message": "Password must be at least 6 characters"
            }), 400
        
        if len(password) > 50:
            return jsonify({
                "status": "error",
                "message": "Password cannot exceed 50 characters"
            }), 400
        
        # Validation: Phone (optional)
        if phone and not re.match(r'^[0-9\-\+\(\)\s]{7,20}$', phone):
            return jsonify({
                "status": "error",
                "message": "Phone format is invalid (7-20 digits)"
            }), 400
        
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        try:
            # Check if email already exists
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                return jsonify({
                    "status": "error",
                    "message": "Email is already registered"
                }), 400
            
            # Hash password using werkzeug
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            
            # Insert new user with all fields
            cursor.execute("""
                INSERT INTO users (name, email, password, phone, bio, created_at)
                VALUES (%s, %s, %s, %s, %s, NOW())
            """, (name, email, hashed_password, phone, bio))
            
            db.commit()
            user_id = cursor.lastrowid
            
            # Fetch complete user data to return
            cursor.execute("""
                SELECT id, name, email, phone, bio, profile_photo, created_at
                FROM users
                WHERE id = %s
            """, (user_id,))
            
            user = cursor.fetchone()
            cursor.close()
            db.close()
            
            if not user:
                return jsonify({
                    "status": "error",
                    "message": "Failed to create user"
                }), 500
            
            return jsonify({
                "status": "success",
                "message": "Registration successful. Please login to continue.",
                "user": {
                    "id": user['id'],
                    "name": user['name'],
                    "email": user['email'],
                    "phone": user['phone'],
                    "bio": user['bio'],
                    "profile_photo": user['profile_photo']
                }
            }), 201
        
        except Exception as db_error:
            db.rollback()
            cursor.close()
            db.close()
            return jsonify({
                "status": "error",
                "message": f"Database error: {str(db_error)}"
            }), 500
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Registration error: {str(e)}"
        }), 500


# LOGIN
@auth_bp.route("/login", methods=["POST"])
def login():
    """
    Login user
    Expected JSON: {
        "email": "user@example.com",
        "password": "password123"
    }
    """
    try:
        data = request.json
        
        # Validate required fields
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({
                "status": "error",
                "message": "Email and password are required"
            }), 400
        
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        # Get user by email
        cursor.execute("SELECT id, name, email, password, role FROM users WHERE email = %s", (data['email'],))
        user = cursor.fetchone()
        cursor.close()
        db.close()
        
        if not user:
            return jsonify({
                "status": "error",
                "message": "User not found"
            }), 401
        
        # Check password
        if not check_password_hash(user['password'], data['password']):
            return jsonify({
                "status": "error",
                "message": "Invalid password"
            }), 401
        
        return jsonify({
            "status": "success",
            "message": "Login successful",
            "user": {
                "id": user['id'],
                "name": user['name'],
                "email": user['email'],
                "role": user['role']
            }
        }), 200
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Login failed: {str(e)}"
        }), 500


# GET USER PROFILE
@auth_bp.route("/profile/<int:user_id>", methods=["GET"])
def get_profile(user_id):
    """Get user profile"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT id, name, email, phone, bio, profile_photo, role, created_at 
            FROM users WHERE id = %s
        """, (user_id,))
        
        user = cursor.fetchone()
        cursor.close()
        db.close()
        
        if not user:
            return jsonify({
                "status": "error",
                "message": "User not found"
            }), 404
        
        return jsonify({
            "status": "success",
            "user": user
        }), 200
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to get profile: {str(e)}"
        }), 500


# UPDATE USER PROFILE
@auth_bp.route("/profile/<int:user_id>", methods=["PUT"])
def update_profile(user_id):
    """
    Update user profile
    Expected JSON: {
        "name": "New Name",
        "phone": "081234567890",
        "bio": "User bio"
    }
    """
    try:
        data = request.json
        
        if not data:
            return jsonify({
                "status": "error",
                "message": "No data provided"
            }), 400
        
        db = get_db()
        cursor = db.cursor()
        
        # Build update query dynamically
        update_fields = []
        update_values = []
        
        if 'name' in data:
            update_fields.append("name = %s")
            update_values.append(data['name'])
        
        if 'phone' in data:
            update_fields.append("phone = %s")
            update_values.append(data['phone'])
        
        if 'bio' in data:
            update_fields.append("bio = %s")
            update_values.append(data['bio'])
        
        if not update_fields:
            return jsonify({
                "status": "error",
                "message": "No fields to update"
            }), 400
        
        update_values.append(user_id)
        query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = %s"
        
        cursor.execute(query, update_values)
        db.commit()
        cursor.close()
        db.close()
        
        return jsonify({
            "status": "success",
            "message": "Profile updated successfully"
        }), 200
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to update profile: {str(e)}"
        }), 500

