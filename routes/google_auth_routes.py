"""
Google OAuth Routes for Ruang Hijau Backend
Handles Google Sign-In authentication from Flutter app
"""

from flask import Blueprint, request, jsonify
from db import get_db
from werkzeug.security import generate_password_hash
import requests
import os

google_auth_bp = Blueprint("google_auth", __name__)

# Google OAuth Configuration
GOOGLE_CLIENT_ID_WEB = os.getenv('GOOGLE_CLIENT_ID_WEB', '186851201326-40k8450mphcd602pq9v4iuvo2tpbb87i.apps.googleusercontent.com')
GOOGLE_CLIENT_ID_FLUTTER = os.getenv('GOOGLE_CLIENT_ID_FLUTTER', '186851201326-j1uo9ctso5hev13t3o4bgrgf1n3cg10q.apps.googleusercontent.com')


def verify_google_token(id_token):
    """
    Verify Google ID token and return user info
    """
    try:
        # Verify token with Google
        response = requests.get(
            f'https://oauth2.googleapis.com/tokeninfo?id_token={id_token}',
            timeout=10
        )
        
        if response.status_code != 200:
            print(f"DEBUG: Google token verification failed: {response.text}")
            return None
        
        token_info = response.json()
        
        # Verify the token is for our app
        if token_info.get('aud') not in [GOOGLE_CLIENT_ID_WEB, GOOGLE_CLIENT_ID_FLUTTER]:
            print(f"DEBUG: Token audience mismatch: {token_info.get('aud')}")
            return None
        
        return token_info
    
    except requests.exceptions.RequestException as e:
        print(f"DEBUG: Google token verification error: {str(e)}")
        return None


def get_google_user_info(access_token):
    """
    Get user info from Google using access token
    """
    try:
        response = requests.get(
            'https://www.googleapis.com/oauth2/v2/userinfo',
            headers={'Authorization': f'Bearer {access_token}'},
            timeout=10
        )
        
        if response.status_code != 200:
            print(f"DEBUG: Failed to get Google user info: {response.text}")
            return None
        
        return response.json()
    
    except requests.exceptions.RequestException as e:
        print(f"DEBUG: Google user info error: {str(e)}")
        return None


@google_auth_bp.route("/google", methods=["POST"])
def google_sign_in():
    """
    Handle Google Sign-In from Flutter app
    
    Expected JSON Options:
    
    Option 1 - Using ID Token (recommended):
    {
        "id_token": "google_id_token_from_flutter"
    }
    
    Option 2 - Using Access Token:
    {
        "access_token": "google_access_token_from_flutter"
    }
    
    Option 3 - Direct user info (for testing or when Google Sign-In already verified on client):
    {
        "google_id": "google_user_id",
        "email": "user@gmail.com",
        "name": "User Name",
        "profile_photo": "https://..." (optional)
    }
    
    Response: 200 OK
    {
        "status": "success",
        "message": "Google login successful",
        "is_new_user": true/false,
        "user": {
            "id": 1,
            "name": "User Name",
            "email": "user@gmail.com",
            "google_id": "google_user_id",
            "profile_photo": "...",
            "role": "user"
        }
    }
    """
    try:
        data = request.json
        
        if not data:
            return jsonify({
                "status": "error",
                "message": "Request body cannot be empty"
            }), 400
        
        google_id = None
        email = None
        name = None
        profile_photo = None
        
        # Option 1: Verify ID Token
        if data.get('id_token'):
            token_info = verify_google_token(data['id_token'])
            if not token_info:
                return jsonify({
                    "status": "error",
                    "message": "Invalid Google ID token"
                }), 401
            
            google_id = token_info.get('sub')
            email = token_info.get('email')
            name = token_info.get('name', email.split('@')[0] if email else 'User')
            profile_photo = token_info.get('picture')
        
        # Option 2: Get user info from access token
        elif data.get('access_token'):
            user_info = get_google_user_info(data['access_token'])
            if not user_info:
                return jsonify({
                    "status": "error",
                    "message": "Invalid Google access token"
                }), 401
            
            google_id = user_info.get('id')
            email = user_info.get('email')
            name = user_info.get('name', email.split('@')[0] if email else 'User')
            profile_photo = user_info.get('picture')
        
        # Option 3: Direct user info (for client-verified Google Sign-In)
        elif data.get('google_id') and data.get('email'):
            google_id = data.get('google_id')
            email = data.get('email')
            name = data.get('name', email.split('@')[0] if email else 'User')
            profile_photo = data.get('profile_photo') or data.get('photo_url')
        
        else:
            return jsonify({
                "status": "error",
                "message": "Either id_token, access_token, or (google_id + email) is required"
            }), 400
        
        # Validate required fields
        if not google_id or not email:
            return jsonify({
                "status": "error",
                "message": "Could not retrieve Google user information"
            }), 400
        
        print(f"DEBUG: Google Sign-In - google_id={google_id}, email={email}, name={name}")
        
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        try:
            is_new_user = False
            
            # Check if user exists by google_id
            cursor.execute("""
                SELECT id, name, email, google_id, profile_photo, role, phone, bio
                FROM users 
                WHERE google_id = %s
            """, (google_id,))
            user = cursor.fetchone()
            
            if not user:
                # Check if user exists by email (might have registered normally before)
                cursor.execute("""
                    SELECT id, name, email, google_id, profile_photo, role, phone, bio
                    FROM users 
                    WHERE email = %s
                """, (email,))
                user = cursor.fetchone()
                
                if user:
                    # Link Google account to existing user
                    cursor.execute("""
                        UPDATE users 
                        SET google_id = %s, 
                            profile_photo = COALESCE(profile_photo, %s),
                            updated_at = NOW()
                        WHERE id = %s
                    """, (google_id, profile_photo, user['id']))
                    db.commit()
                    
                    # Refresh user data
                    cursor.execute("""
                        SELECT id, name, email, google_id, profile_photo, role, phone, bio
                        FROM users 
                        WHERE id = %s
                    """, (user['id'],))
                    user = cursor.fetchone()
                else:
                    # Create new user
                    is_new_user = True
                    
                    # Generate a random password for Google users (they won't use it)
                    random_password = generate_password_hash(f"google_{google_id}_{email}", method='pbkdf2:sha256')
                    
                    cursor.execute("""
                        INSERT INTO users (name, email, password, google_id, profile_photo, role, created_at)
                        VALUES (%s, %s, %s, %s, %s, 'user', NOW())
                    """, (name, email, random_password, google_id, profile_photo))
                    db.commit()
                    
                    user_id = cursor.lastrowid
                    
                    # Fetch created user
                    cursor.execute("""
                        SELECT id, name, email, google_id, profile_photo, role, phone, bio
                        FROM users 
                        WHERE id = %s
                    """, (user_id,))
                    user = cursor.fetchone()
            else:
                # Update profile photo if changed
                if profile_photo and user.get('profile_photo') != profile_photo:
                    cursor.execute("""
                        UPDATE users 
                        SET profile_photo = %s, updated_at = NOW()
                        WHERE id = %s
                    """, (profile_photo, user['id']))
                    db.commit()
                    user['profile_photo'] = profile_photo
            
            cursor.close()
            db.close()
            
            if not user:
                return jsonify({
                    "status": "error",
                    "message": "Failed to create or find user"
                }), 500
            
            return jsonify({
                "status": "success",
                "message": "Google login successful",
                "is_new_user": is_new_user,
                "user": {
                    "id": user['id'],
                    "name": user['name'],
                    "email": user['email'],
                    "google_id": user.get('google_id'),
                    "profile_photo": user.get('profile_photo'),
                    "phone": user.get('phone'),
                    "bio": user.get('bio'),
                    "role": user.get('role', 'user')
                }
            }), 200
        
        except Exception as db_error:
            db.rollback()
            cursor.close()
            db.close()
            print(f"DEBUG: Database error in Google Sign-In: {str(db_error)}")
            return jsonify({
                "status": "error",
                "message": f"Database error: {str(db_error)}"
            }), 500
    
    except Exception as e:
        print(f"DEBUG: Google Sign-In error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Google login failed: {str(e)}"
        }), 500


@google_auth_bp.route("/google/verify", methods=["POST"])
def verify_google_user():
    """
    Verify if a Google user exists in the system
    
    Expected JSON:
    {
        "google_id": "google_user_id"
    }
    OR
    {
        "email": "user@gmail.com"
    }
    
    Response: 200 OK
    {
        "status": "success",
        "exists": true/false,
        "user": {...} (if exists)
    }
    """
    try:
        data = request.json
        
        if not data:
            return jsonify({
                "status": "error",
                "message": "Request body cannot be empty"
            }), 400
        
        google_id = data.get('google_id')
        email = data.get('email')
        
        if not google_id and not email:
            return jsonify({
                "status": "error",
                "message": "Either google_id or email is required"
            }), 400
        
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        if google_id:
            cursor.execute("""
                SELECT id, name, email, google_id, profile_photo, role
                FROM users 
                WHERE google_id = %s
            """, (google_id,))
        else:
            cursor.execute("""
                SELECT id, name, email, google_id, profile_photo, role
                FROM users 
                WHERE email = %s
            """, (email,))
        
        user = cursor.fetchone()
        cursor.close()
        db.close()
        
        if user:
            return jsonify({
                "status": "success",
                "exists": True,
                "user": user
            }), 200
        else:
            return jsonify({
                "status": "success",
                "exists": False,
                "user": None
            }), 200
    
    except Exception as e:
        print(f"DEBUG: Verify Google user error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Verification failed: {str(e)}"
        }), 500
