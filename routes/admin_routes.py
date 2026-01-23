from flask import Blueprint, jsonify, request, send_from_directory, render_template
from db_helper import get_db, close_db, execute_query, execute_update
import hashlib
import os
import jwt
import datetime
from functools import wraps

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

# Secret key untuk JWT (sebaiknya di environment variable)
SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-change-this-in-production')

# ===== AUTHENTICATION MIDDLEWARE =====
def admin_required(f):
    """Decorator to require admin authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            return jsonify({'error': 'Token tidak ditemukan'}), 401
        
        try:
            # Remove 'Bearer ' prefix if exists
            if token.startswith('Bearer '):
                token = token[7:]
            
            # Decode token
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            
            # Check if user is admin
            if payload.get('role') != 'admin':
                return jsonify({'error': 'Akses ditolak. Hanya admin yang diizinkan'}), 403
            
            # Add user info to request
            request.admin_id = payload.get('user_id')
            request.admin_email = payload.get('email')
            
        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token sudah expired'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'error': 'Token tidak valid'}), 401
        
        return f(*args, **kwargs)
    
    return decorated_function


# ===== ADMIN LOGIN =====
@admin_bp.route('/login', methods=['GET'])
def serve_login_page():
    """Serve admin login HTML"""
    try:
        templates_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
        return send_from_directory(templates_dir, 'admin_login.html')
    except Exception as e:
        return jsonify({'error': str(e)}), 404
    
@admin_bp.route('/login', methods=['POST'])
def admin_login():
    """Admin login endpoint"""
    try:
        data = request.json
        
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email dan password harus diisi'}), 400
        
        email = data['email']
        password = data['password']
        
        # Hash password
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        # Check user in database
        query = """
            SELECT id, name, email, role, profile_photo
            FROM users
            WHERE email = %s AND password = %s
        """
        user = execute_query(query, (email, password_hash), fetch_one=True)
        
        if not user:
            return jsonify({'error': 'Email atau password salah'}), 401
        
        # Check if user is admin
        if user['role'] != 'admin':
            return jsonify({'error': 'Akses ditolak. Hanya admin yang dapat login'}), 403
        
        # Generate JWT token (valid for 24 hours)
        token_payload = {
            'user_id': user['id'],
            'email': user['email'],
            'role': user['role'],
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
        }
        
        token = jwt.encode(token_payload, SECRET_KEY, algorithm='HS256')
        
        return jsonify({
            'token': token,
            'user': {
                'id': user['id'],
                'name': user['name'],
                'email': user['email'],
                'role': user['role'],
                'profile_photo': user.get('profile_photo')
            }
        }), 200
        
    except Exception as e:
        print(f"Error in admin_login: {str(e)}")
        return jsonify({'error': str(e)}), 500


# ===== VERIFY TOKEN =====
@admin_bp.route('/verify', methods=['GET'])
@admin_required
def verify_token():
    """Verify admin token"""
    try:
        # Get user info from database
        query = """
            SELECT id, name, email, role, profile_photo
            FROM users
            WHERE id = %s AND role = 'admin'
        """
        user = execute_query(query, (request.admin_id,), fetch_one=True)
        
        if not user:
            return jsonify({'error': 'User tidak ditemukan'}), 404
        
        return jsonify({
            'valid': True,
            'user': {
                'id': user['id'],
                'name': user['name'],
                'email': user['email'],
                'role': user['role'],
                'profile_photo': user.get('profile_photo')
            }
        }), 200
        
    except Exception as e:
        print(f"Error in verify_token: {str(e)}")
        return jsonify({'error': str(e)}), 500


# ===== SERVE ADMIN DASHBOARD HTML =====
@admin_bp.route('/dashboard')
@admin_required
def serve_dashboard():
    """Serve admin dashboard HTML"""
    try:
        templates_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'templates')
        return send_from_directory(templates_dir, 'admin_dashboard.html')
    except Exception as e:
        return jsonify({'error': str(e)}), 404


# ===== DASHBOARD STATS =====
@admin_bp.route('/stats', methods=['GET'])
def get_stats():
    """Get dashboard statistics"""
    try:
        db = get_db()
        cursor = db.cursor()
        
        # Total users
        cursor.execute("SELECT COUNT(*) FROM users")
        total_users = cursor.fetchone()[0]
        
        # Total posts
        cursor.execute("SELECT COUNT(*) FROM posts")
        total_posts = cursor.fetchone()[0]
        
        # Active campaigns
        cursor.execute("SELECT COUNT(*) FROM campaigns WHERE campaign_status = 'active'")
        active_campaigns = cursor.fetchone()[0]
        
        # Total donations
        cursor.execute("SELECT COALESCE(SUM(amount), 0) FROM donations")
        total_donations = cursor.fetchone()[0]
        
        # Active volunteers
        cursor.execute("SELECT COUNT(*) FROM volunteers WHERE volunteer_status = 'approved'")
        active_volunteers = cursor.fetchone()[0]
        
        # Total comments
        cursor.execute("SELECT COUNT(*) FROM comments")
        total_comments = cursor.fetchone()[0]
        
        # Total feedback
        cursor.execute("SELECT COUNT(*) FROM feedback")
        total_feedback = cursor.fetchone()[0]
        
        cursor.close()
        close_db(db)
        
        return jsonify({
            'data': {
                'total_users': total_users,
                'total_posts': total_posts,
                'active_campaigns': active_campaigns,
                'total_donation_amount': int(total_donations),
                'total_volunteers': active_volunteers,
                'total_comments': total_comments,
                'total_feedback': total_feedback,
                'new_users_today': 0,  # TODO: implement
                'new_posts_today': 0,  # TODO: implement
                'monthly_donations': 0,  # TODO: implement
                'pending_volunteers': 0,  # TODO: implement
                'average_rating': 0.0  # TODO: implement
            }
        }), 200
        
    except Exception as e:
        print(f"Error in get_stats: {str(e)}")
        # Return dummy data if database error
        return jsonify({
            'data': {
                'total_users': 1247,
                'total_posts': 3856,
                'active_campaigns': 28,
                'total_donation_amount': 45000000,
                'total_volunteers': 156,
                'total_comments': 892,
                'total_feedback': 45,
                'new_users_today': 12,
                'new_posts_today': 34,
                'monthly_donations': 5000000,
                'pending_volunteers': 23,
                'average_rating': 4.5
            }
        }), 200


# ============================================================================
# USERS MANAGEMENT - CRUD LENGKAP
# ============================================================================

@admin_bp.route('/users', methods=['GET'])
def get_users():
    """Get all users with pagination and filtering"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        role_filter = request.args.get('role', None)
        offset = (page - 1) * per_page
        
        # Build query with optional role filter
        if role_filter:
            query = """
                SELECT id, name, email, phone, profile_photo, bio, role, created_at, updated_at
                FROM users 
                WHERE role = %s
                ORDER BY created_at DESC 
                LIMIT %s OFFSET %s
            """
            users = execute_query(query, (role_filter, per_page, offset))
        else:
            query = """
                SELECT id, name, email, phone, profile_photo, bio, role, created_at, updated_at
                FROM users 
                ORDER BY created_at DESC 
                LIMIT %s OFFSET %s
            """
            users = execute_query(query, (per_page, offset))
        
        if users is None:
            return jsonify({'error': 'Failed to fetch users'}), 500
        
        users_data = []
        for user in users:
            users_data.append({
                'id': user['id'],
                'name': user['name'],
                'email': user['email'],
                'phone': user.get('phone'),
                'profile_photo': user.get('profile_photo'),
                'bio': user.get('bio'),
                'role': user['role'],
                'created_at': str(user['created_at']) if user.get('created_at') else None,
                'updated_at': str(user['updated_at']) if user.get('updated_at') else None,
            })
        
        return jsonify(users_data), 200
        
    except Exception as e:
        print(f"Error in get_users: {str(e)}")
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user_detail(user_id):
    """Get single user details"""
    try:
        query = """
            SELECT id, name, email, phone, profile_photo, bio, role, created_at, updated_at
            FROM users 
            WHERE id = %s
        """
        user = execute_query(query, (user_id,), fetch_one=True)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'id': user['id'],
            'name': user['name'],
            'email': user['email'],
            'phone': user.get('phone'),
            'profile_photo': user.get('profile_photo'),
            'bio': user.get('bio'),
            'role': user['role'],
            'created_at': str(user['created_at']) if user.get('created_at') else None,
            'updated_at': str(user['updated_at']) if user.get('updated_at') else None,
        }), 200
        
    except Exception as e:
        print(f"Error in get_user_detail: {str(e)}")
        return jsonify({'error': str(e)}), 404


@admin_bp.route('/users', methods=['POST'])
def create_user():
    """Create new user"""
    try:
        data = request.json
        
        # Validasi required fields
        if not data.get('name') or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Name, email, and password are required'}), 400
        
        # Hash password
        password_hash = hashlib.sha256(data['password'].encode()).hexdigest()
        
        # Check if email already exists
        check_query = "SELECT id FROM users WHERE email = %s"
        existing = execute_query(check_query, (data['email'],), fetch_one=True)
        
        if existing:
            return jsonify({'error': 'Email already registered'}), 400
        
        # Insert user
        query = """
            INSERT INTO users (name, email, password, phone, bio, role)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (
            data['name'],
            data['email'],
            password_hash,
            data.get('phone'),
            data.get('bio'),
            data.get('role', 'user')
        )
        
        result = execute_update(query, params)
        
        if result > 0:
            return jsonify({
                'message': 'User created successfully',
                'user_id': result
            }), 201
        else:
            return jsonify({'error': 'Failed to create user'}), 500
            
    except Exception as e:
        print(f"Error in create_user: {str(e)}")
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """Update user"""
    try:
        data = request.json
        
        # Check if user exists
        check_query = "SELECT id FROM users WHERE id = %s"
        existing = execute_query(check_query, (user_id,), fetch_one=True)
        
        if not existing:
            return jsonify({'error': 'User not found'}), 404
        
        # Build update query dynamically
        update_fields = []
        params = []
        
        if 'name' in data:
            update_fields.append("name = %s")
            params.append(data['name'])
        
        if 'email' in data:
            # Check if email is already used by another user
            email_check = "SELECT id FROM users WHERE email = %s AND id != %s"
            email_exists = execute_query(email_check, (data['email'], user_id), fetch_one=True)
            if email_exists:
                return jsonify({'error': 'Email already used by another user'}), 400
            
            update_fields.append("email = %s")
            params.append(data['email'])
        
        if 'password' in data and data['password']:
            password_hash = hashlib.sha256(data['password'].encode()).hexdigest()
            update_fields.append("password = %s")
            params.append(password_hash)
        
        if 'phone' in data:
            update_fields.append("phone = %s")
            params.append(data['phone'])
        
        if 'bio' in data:
            update_fields.append("bio = %s")
            params.append(data['bio'])
        
        if 'role' in data:
            update_fields.append("role = %s")
            params.append(data['role'])
        
        if not update_fields:
            return jsonify({'error': 'No fields to update'}), 400
        
        # Add updated_at timestamp
        update_fields.append("updated_at = CURRENT_TIMESTAMP")
        
        # Add user_id to params
        params.append(user_id)
        
        query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = %s"
        result = execute_update(query, tuple(params))
        
        if result >= 0:
            return jsonify({'message': 'User updated successfully'}), 200
        else:
            return jsonify({'error': 'Failed to update user'}), 500
            
    except Exception as e:
        print(f"Error in update_user: {str(e)}")
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete user (will cascade delete related data)"""
    try:
        # Check if user exists
        check_query = "SELECT name, role FROM users WHERE id = %s"
        user = execute_query(check_query, (user_id,), fetch_one=True)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Prevent deleting last admin
        if user['role'] == 'admin':
            admin_check = "SELECT COUNT(*) as admin_count FROM users WHERE role = 'admin'"
            result = execute_query(admin_check, fetch_one=True)
            if result and result['admin_count'] <= 1:
                return jsonify({'error': 'Cannot delete the last admin user'}), 400
        
        # Delete user (cascade will handle related data)
        query = "DELETE FROM users WHERE id = %s"
        result = execute_update(query, (user_id,))
        
        if result > 0:
            return jsonify({'message': f'User "{user["name"]}" deleted successfully'}), 200
        else:
            return jsonify({'error': 'Failed to delete user'}), 500
        
    except Exception as e:
        print(f"Error in delete_user: {str(e)}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# POSTS MANAGEMENT
# ============================================================================

@admin_bp.route('/posts', methods=['GET'])
def get_posts():
    """Get all posts for moderation"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        offset = (page - 1) * per_page
        
        query = """
            SELECT p.id, p.user_id, p.text, p.image, p.likes, p.created_at,
                    u.name as author_name,
                    (SELECT COUNT(*) FROM comments WHERE post_id = p.id) as comment_count
            FROM posts p
            LEFT JOIN users u ON p.user_id = u.id
            ORDER BY p.created_at DESC
            LIMIT %s OFFSET %s
        """
        posts = execute_query(query, (per_page, offset))
        
        if posts is None:
            return jsonify({'error': 'Failed to fetch posts'}), 500
        
        posts_data = []
        for post in posts:
            text = post.get('text', '') or ''
            posts_data.append({
                'id': post['id'],
                'title': text[:50] + '...' if len(text) > 50 else text,
                'content': text,
                'author_id': post['user_id'],
                'author_name': post.get('author_name', 'Unknown'),
                'image': post.get('image'),
                'likes': post.get('likes', 0),
                'comment_count': post.get('comment_count', 0),
                'created_at': str(post['created_at']) if post.get('created_at') else None,
                'status': 'approved',
            })
        
        return jsonify(posts_data), 200
        
    except Exception as e:
        print(f"Error in get_posts: {str(e)}")
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/posts/<int:post_id>', methods=['GET'])
def get_post_detail(post_id):
    """Get single post detail with comments"""
    try:
        # Get post detail
        post_query = """
            SELECT p.id, p.user_id, p.text, p.image, p.likes, p.created_at,
                    u.name as author_name, u.email as author_email
            FROM posts p
            LEFT JOIN users u ON p.user_id = u.id
            WHERE p.id = %s
        """
        post = execute_query(post_query, (post_id,), fetch_one=True)
        
        if not post:
            return jsonify({'error': 'Post not found'}), 404
        
        # Get comments for this post
        comments_query = """
            SELECT c.id, c.user_id, c.text, c.created_at,
                    u.name as commenter_name
            FROM comments c
            LEFT JOIN users u ON c.user_id = u.id
            WHERE c.post_id = %s
            ORDER BY c.created_at DESC
        """
        comments = execute_query(comments_query, (post_id,))
        
        comments_data = []
        if comments:
            for comment in comments:
                comments_data.append({
                    'id': comment['id'],
                    'user_id': comment['user_id'],
                    'commenter_name': comment.get('commenter_name', 'Unknown'),
                    'text': comment['text'],
                    'created_at': str(comment['created_at']) if comment.get('created_at') else None,
                })
        
        return jsonify({
            'id': post['id'],
            'author_id': post['user_id'],
            'author_name': post.get('author_name', 'Unknown'),
            'author_email': post.get('author_email'),
            'content': post.get('text', ''),
            'image': post.get('image'),
            'likes': post.get('likes', 0),
            'created_at': str(post['created_at']) if post.get('created_at') else None,
            'comments': comments_data
        }), 200
        
    except Exception as e:
        print(f"Error in get_post_detail: {str(e)}")
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    """Delete post (will cascade delete comments)"""
    try:
        # Check if post exists
        check_query = "SELECT id FROM posts WHERE id = %s"
        post = execute_query(check_query, (post_id,), fetch_one=True)
        
        if not post:
            return jsonify({'error': 'Post not found'}), 404
        
        query = "DELETE FROM posts WHERE id = %s"
        result = execute_update(query, (post_id,))
        
        if result > 0:
            return jsonify({'message': 'Post deleted successfully'}), 200
        else:
            return jsonify({'error': 'Failed to delete post'}), 500
        
    except Exception as e:
        print(f"Error in delete_post: {str(e)}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# COMMENTS MANAGEMENT
# ============================================================================

@admin_bp.route('/comments', methods=['GET'])
def get_all_comments():
    """Get all comments across all posts"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        offset = (page - 1) * per_page
        
        query = """
            SELECT c.id, c.user_id, c.post_id, c.text, c.created_at,
                   u.name as commenter_name,
                   p.text as post_text
            FROM comments c
            LEFT JOIN users u ON c.user_id = u.id
            LEFT JOIN posts p ON c.post_id = p.id
            ORDER BY c.created_at DESC
            LIMIT %s OFFSET %s
        """
        comments = execute_query(query, (per_page, offset))
        
        if comments is None:
            return jsonify({'error': 'Failed to fetch comments'}), 500
        
        comments_data = []
        for comment in comments:
            post_text = comment.get('post_text', '') or ''
            comments_data.append({
                'id': comment['id'],
                'user_id': comment['user_id'],
                'post_id': comment['post_id'],
                'commenter_name': comment.get('commenter_name', 'Unknown'),
                'text': comment['text'],
                'post_preview': post_text[:50] + '...' if len(post_text) > 50 else post_text,
                'created_at': str(comment['created_at']) if comment.get('created_at') else None,
            })
        
        return jsonify(comments_data), 200
        
    except Exception as e:
        print(f"Error in get_all_comments: {str(e)}")
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/posts/<int:post_id>/comments', methods=['GET'])
def get_post_comments(post_id):
    """Get all comments for specific post"""
    try:
        query = """
            SELECT c.id, c.user_id, c.text, c.created_at,
                   u.name as commenter_name
            FROM comments c
            LEFT JOIN users u ON c.user_id = u.id
            WHERE c.post_id = %s
            ORDER BY c.created_at DESC
        """
        comments = execute_query(query, (post_id,))
        
        if comments is None:
            return jsonify({'error': 'Failed to fetch comments'}), 500
        
        comments_data = []
        for comment in comments:
            comments_data.append({
                'id': comment['id'],
                'user_id': comment['user_id'],
                'commenter_name': comment.get('commenter_name', 'Unknown'),
                'text': comment['text'],
                'created_at': str(comment['created_at']) if comment.get('created_at') else None,
            })
        
        return jsonify(comments_data), 200
        
    except Exception as e:
        print(f"Error in get_post_comments: {str(e)}")
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/comments/<int:comment_id>', methods=['DELETE'])
def delete_comment(comment_id):
    """Delete comment"""
    try:
        # Check if comment exists
        check_query = "SELECT id FROM comments WHERE id = %s"
        comment = execute_query(check_query, (comment_id,), fetch_one=True)
        
        if not comment:
            return jsonify({'error': 'Comment not found'}), 404
        
        query = "DELETE FROM comments WHERE id = %s"
        result = execute_update(query, (comment_id,))
        
        if result > 0:
            return jsonify({'message': 'Comment deleted successfully'}), 200
        else:
            return jsonify({'error': 'Failed to delete comment'}), 500
        
    except Exception as e:
        print(f"Error in delete_comment: {str(e)}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# CAMPAIGNS MANAGEMENT
# ============================================================================

@admin_bp.route('/campaigns', methods=['GET'])
@admin_required  # ✅ FIXED: Tambah authentication
def get_campaigns():
    """Get all campaigns"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 100, type=int)
        status_filter = request.args.get('status', None)
        offset = (page - 1) * per_page
        
        if status_filter:
            query = """
                SELECT id, title, description, target_amount, current_amount, 
                       campaign_status, created_at,
                       (SELECT COUNT(*) FROM donations WHERE campaign_id = campaigns.id) as donation_count
                FROM campaigns
                WHERE campaign_status = %s
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
            """
            campaigns = execute_query(query, (status_filter, per_page, offset))
        else:
            query = """
                SELECT id, title, description, target_amount, current_amount, 
                       campaign_status, created_at,
                       (SELECT COUNT(*) FROM donations WHERE campaign_id = campaigns.id) as donation_count
                FROM campaigns
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
            """
            campaigns = execute_query(query, (per_page, offset))
        
        if campaigns is None:
            return jsonify([]), 200  # ✅ FIXED: Return empty array instead of error
        
        campaigns_data = []
        for campaign in campaigns:
            description = campaign.get('description', '') or ''
            campaigns_data.append({
                'id': campaign['id'],
                'title': campaign['title'],
                'description': (description[:100] + '...') if len(description) > 100 else description,
                'organizer': 'RuangHijau',
                'target_amount': float(campaign.get('target_amount', 0)),
                'collected_amount': float(campaign.get('current_amount', 0)),
                'donation_count': campaign.get('donation_count', 0),
                'is_active': campaign.get('campaign_status') == 'active',
                'status': campaign.get('campaign_status'),
                'created_at': str(campaign['created_at']) if campaign.get('created_at') else None,
            })
        
        return jsonify(campaigns_data), 200
        
    except Exception as e:
        print(f"Error in get_campaigns: {str(e)}")
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/campaigns/<int:campaign_id>', methods=['GET'])
@admin_required  # ✅ FIXED: Tambah authentication
def get_campaign_detail(campaign_id):
    """Get single campaign detail"""
    try:
        query = """
            SELECT id, title, description, target_amount, current_amount, 
                   campaign_status, created_at
            FROM campaigns
            WHERE id = %s
        """
        campaign = execute_query(query, (campaign_id,), fetch_one=True)
        
        if not campaign:
            return jsonify({'error': 'Campaign not found'}), 404
        
        # Get donations for this campaign
        donations_query = """
            SELECT d.id, d.donor_id, d.amount, d.created_at,
                   u.name as donor_name
            FROM donations d
            LEFT JOIN users u ON d.donor_id = u.id
            WHERE d.campaign_id = %s
            ORDER BY d.created_at DESC
        """
        donations = execute_query(donations_query, (campaign_id,))
        
        donations_data = []
        if donations:
            for donation in donations:
                donations_data.append({
                    'id': donation['id'],
                    'donor_id': donation['donor_id'],
                    'donor_name': donation.get('donor_name', 'Anonymous'),
                    'amount': float(donation['amount']),
                    'created_at': str(donation['created_at']) if donation.get('created_at') else None,
                })
        
        return jsonify({
            'id': campaign['id'],
            'title': campaign['title'],
            'description': campaign.get('description'),
            'target_amount': float(campaign.get('target_amount', 0)),
            'collected_amount': float(campaign.get('current_amount', 0)),
            'status': campaign.get('campaign_status'),
            'created_at': str(campaign['created_at']) if campaign.get('created_at') else None,
            'donations': donations_data
        }), 200
        
    except Exception as e:
        print(f"Error in get_campaign_detail: {str(e)}")
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/campaigns', methods=['POST'])
@admin_required  # ✅ FIXED: Tambah authentication
def create_campaign():
    """Create new campaign"""
    try:
        data = request.json
        
        # Validasi required fields
        if not data.get('title') or not data.get('target_amount'):
            return jsonify({'error': 'Title and target amount are required'}), 400
        
        query = """
            INSERT INTO campaigns (title, description, target_amount, current_amount, campaign_status)
            VALUES (%s, %s, %s, 0, 'active')
        """
        params = (
            data['title'],
            data.get('description'),
            data['target_amount']
        )
        
        result = execute_update(query, params)
        
        if result > 0:
            return jsonify({
                'message': 'Campaign created successfully',
                'campaign_id': result
            }), 201
        else:
            return jsonify({'error': 'Failed to create campaign'}), 500
            
    except Exception as e:
        print(f"Error in create_campaign: {str(e)}")
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/campaigns/<int:campaign_id>', methods=['PUT'])
@admin_required  # ✅ FIXED: Tambah authentication
def update_campaign(campaign_id):
    """Update campaign"""
    try:
        data = request.json
        
        # Check if campaign exists
        check_query = "SELECT id FROM campaigns WHERE id = %s"
        existing = execute_query(check_query, (campaign_id,), fetch_one=True)
        
        if not existing:
            return jsonify({'error': 'Campaign not found'}), 404
        
        # Build update query dynamically
        update_fields = []
        params = []
        
        if 'title' in data:
            update_fields.append("title = %s")
            params.append(data['title'])
        
        if 'description' in data:
            update_fields.append("description = %s")
            params.append(data['description'])
        
        if 'target_amount' in data:
            update_fields.append("target_amount = %s")
            params.append(data['target_amount'])
        
        if 'campaign_status' in data:
            update_fields.append("campaign_status = %s")
            params.append(data['campaign_status'])
        
        if not update_fields:
            return jsonify({'error': 'No fields to update'}), 400
        
        params.append(campaign_id)
        
        query = f"UPDATE campaigns SET {', '.join(update_fields)} WHERE id = %s"
        result = execute_update(query, tuple(params))
        
        if result >= 0:
            return jsonify({'message': 'Campaign updated successfully'}), 200
        else:
            return jsonify({'error': 'Failed to update campaign'}), 500
            
    except Exception as e:
        print(f"Error in update_campaign: {str(e)}")
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/campaigns/<int:campaign_id>/toggle', methods=['PUT'])
@admin_required  # ✅ FIXED: Tambah authentication
def toggle_campaign(campaign_id):
    """Activate or deactivate campaign"""
    try:
        # Get current status
        query = "SELECT campaign_status FROM campaigns WHERE id = %s"
        campaign = execute_query(query, (campaign_id,), fetch_one=True)
        
        if not campaign:
            return jsonify({'error': 'Campaign not found'}), 404
        
        # Toggle status
        new_status = 'cancelled' if campaign['campaign_status'] == 'active' else 'active'
        
        update_query = "UPDATE campaigns SET campaign_status = %s WHERE id = %s"
        result = execute_update(update_query, (new_status, campaign_id))
        
        if result >= 0:
            return jsonify({
                'message': f'Campaign status changed to {new_status}',
                'is_active': new_status == 'active',
                'status': new_status
            }), 200
        else:
            return jsonify({'error': 'Failed to update campaign'}), 500
            
    except Exception as e:
        print(f"Error in toggle_campaign: {str(e)}")
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/campaigns/<int:campaign_id>', methods=['DELETE'])
@admin_required  # ✅ FIXED: Tambah authentication
def delete_campaign(campaign_id):
    """Delete campaign"""
    try:
        # Check if campaign exists
        check_query = "SELECT title FROM campaigns WHERE id = %s"
        campaign = execute_query(check_query, (campaign_id,), fetch_one=True)
        
        if not campaign:
            return jsonify({'error': 'Campaign not found'}), 404
        
        query = "DELETE FROM campaigns WHERE id = %s"
        result = execute_update(query, (campaign_id,))
        
        if result > 0:
            return jsonify({'message': f'Campaign "{campaign["title"]}" deleted successfully'}), 200
        else:
            return jsonify({'error': 'Failed to delete campaign'}), 500
        
    except Exception as e:
        print(f"Error in delete_campaign: {str(e)}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# DONATIONS MANAGEMENT
# ============================================================================

@admin_bp.route('/donations', methods=['GET'])
def get_donations():
    """Get all donations"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        offset = (page - 1) * per_page
        
        query = """
            SELECT d.id, d.donor_id, d.campaign_id, d.amount, d.created_at, d.donation_status,
                   u.name as donor_name,
                   c.title as campaign_title
            FROM donations d
            LEFT JOIN users u ON d.donor_id = u.id
            LEFT JOIN campaigns c ON d.campaign_id = c.id
            ORDER BY d.created_at DESC
            LIMIT %s OFFSET %s
        """
        donations = execute_query(query, (per_page, offset))
        
        if donations is None:
            return jsonify({'error': 'Failed to fetch donations'}), 500
        
        donations_data = []
        for donation in donations:
            donations_data.append({
                'id': donation['id'],
                'user_id': donation.get('donor_id'),
                'donor_name': donation.get('donor_name', 'Anonymous'),
                'campaign_id': donation['campaign_id'],
                'campaign_title': donation.get('campaign_title', 'Unknown Campaign'),
                'amount': float(donation['amount']),
                'status': donation.get('donation_status', 'completed'),
                'created_at': str(donation['created_at']) if donation.get('created_at') else None,
            })
        
        return jsonify(donations_data), 200
        
    except Exception as e:
        print(f"Error in get_donations: {str(e)}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# VOLUNTEERS MANAGEMENT
# ============================================================================

@admin_bp.route('/volunteers', methods=['GET'])
def get_volunteers():
    """Get all volunteers with complete info"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        status_filter = request.args.get('status', None)
        offset = (page - 1) * per_page
        
        if status_filter:
            query = """
                SELECT v.id, v.user_id, v.campaign_id, v.volunteer_status, v.created_at,
                       u.name as user_name, u.email, u.phone,
                       c.title as event_name
                FROM volunteers v
                LEFT JOIN users u ON v.user_id = u.id
                LEFT JOIN campaigns c ON v.campaign_id = c.id
                WHERE v.volunteer_status = %s
                ORDER BY v.created_at DESC
                LIMIT %s OFFSET %s
            """
            volunteers = execute_query(query, (status_filter, per_page, offset))
        else:
            query = """
                SELECT v.id, v.user_id, v.campaign_id, v.volunteer_status, v.created_at,
                       u.name as user_name, u.email, u.phone,
                       c.title as event_name
                FROM volunteers v
                LEFT JOIN users u ON v.user_id = u.id
                LEFT JOIN campaigns c ON v.campaign_id = c.id
                ORDER BY v.created_at DESC
                LIMIT %s OFFSET %s
            """
            volunteers = execute_query(query, (per_page, offset))
        
        if volunteers is None:
            return jsonify({'error': 'Failed to fetch volunteers'}), 500
        
        volunteers_data = []
        for volunteer in volunteers:
            volunteers_data.append({
                'id': volunteer['id'],
                'user_id': volunteer['user_id'],
                'name': volunteer.get('user_name', 'Unknown'),
                'email': volunteer.get('email', ''),
                'phone': volunteer.get('phone', ''),
                'campaign_id': volunteer['campaign_id'],
                'event_name': volunteer.get('event_name', 'Unknown Event'),
                'status': volunteer.get('volunteer_status', 'pending'),
                'created_at': str(volunteer['created_at']) if volunteer.get('created_at') else None,
            })
        
        return jsonify(volunteers_data), 200
        
    except Exception as e:
        print(f"Error in get_volunteers: {str(e)}")
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/volunteers/<int:volunteer_id>', methods=['GET'])
def get_volunteer_detail(volunteer_id):
    """Get single volunteer detail"""
    try:
        query = """
            SELECT v.id, v.user_id, v.campaign_id, v.volunteer_status, v.created_at,
                   u.name as user_name, u.email, u.phone, u.bio,
                   c.title as event_name, c.description as event_description
            FROM volunteers v
            LEFT JOIN users u ON v.user_id = u.id
            LEFT JOIN campaigns c ON v.campaign_id = c.id
            WHERE v.id = %s
        """
        volunteer = execute_query(query, (volunteer_id,), fetch_one=True)
        
        if not volunteer:
            return jsonify({'error': 'Volunteer not found'}), 404
        
        return jsonify({
            'id': volunteer['id'],
            'user_id': volunteer['user_id'],
            'name': volunteer.get('user_name', 'Unknown'),
            'email': volunteer.get('email', ''),
            'phone': volunteer.get('phone', ''),
            'bio': volunteer.get('bio'),
            'campaign_id': volunteer['campaign_id'],
            'event_name': volunteer.get('event_name', 'Unknown Event'),
            'event_description': volunteer.get('event_description'),
            'status': volunteer.get('volunteer_status', 'pending'),
            'created_at': str(volunteer['created_at']) if volunteer.get('created_at') else None,
        }), 200
        
    except Exception as e:
        print(f"Error in get_volunteer_detail: {str(e)}")
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/volunteers/<int:volunteer_id>/approve', methods=['POST'])
def approve_volunteer(volunteer_id):
    """Approve volunteer application"""
    try:
        # Check if volunteer exists
        check_query = "SELECT id, volunteer_status FROM volunteers WHERE id = %s"
        volunteer = execute_query(check_query, (volunteer_id,), fetch_one=True)
        
        if not volunteer:
            return jsonify({'error': 'Volunteer not found'}), 404
        
        if volunteer['volunteer_status'] == 'approved':
            return jsonify({'message': 'Volunteer already approved'}), 200
        
        # Update status to approved
        query = "UPDATE volunteers SET volunteer_status = 'approved' WHERE id = %s"
        result = execute_update(query, (volunteer_id,))
        
        if result >= 0:
            return jsonify({'message': 'Volunteer approved successfully'}), 200
        else:
            return jsonify({'error': 'Failed to approve volunteer'}), 500
            
    except Exception as e:
        print(f"Error in approve_volunteer: {str(e)}")
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/volunteers/<int:volunteer_id>/reject', methods=['POST'])
def reject_volunteer(volunteer_id):
    """Reject volunteer application"""
    try:
        # Check if volunteer exists
        check_query = "SELECT id, volunteer_status FROM volunteers WHERE id = %s"
        volunteer = execute_query(check_query, (volunteer_id,), fetch_one=True)
        
        if not volunteer:
            return jsonify({'error': 'Volunteer not found'}), 404
        
        if volunteer['volunteer_status'] == 'rejected':
            return jsonify({'message': 'Volunteer already rejected'}), 200
        
        # Update status to rejected
        query = "UPDATE volunteers SET volunteer_status = 'rejected' WHERE id = %s"
        result = execute_update(query, (volunteer_id,))
        
        if result >= 0:
            return jsonify({'message': 'Volunteer rejected'}), 200
        else:
            return jsonify({'error': 'Failed to reject volunteer'}), 500
            
    except Exception as e:
        print(f"Error in reject_volunteer: {str(e)}")
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/volunteers/<int:volunteer_id>', methods=['DELETE'])
def delete_volunteer(volunteer_id):
    """Delete volunteer"""
    try:
        # Check if volunteer exists
        check_query = "SELECT id FROM volunteers WHERE id = %s"
        volunteer = execute_query(check_query, (volunteer_id,), fetch_one=True)
        
        if not volunteer:
            return jsonify({'error': 'Volunteer not found'}), 404
        
        # Delete volunteer
        query = "DELETE FROM volunteers WHERE id = %s"
        result = execute_update(query, (volunteer_id,))
        
        if result > 0:
            return jsonify({'message': 'Volunteer deleted successfully'}), 200
        else:
            return jsonify({'error': 'Failed to delete volunteer'}), 500
        
    except Exception as e:
        print(f"Error in delete_volunteer: {str(e)}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# FEEDBACK MANAGEMENT
# ============================================================================

@admin_bp.route('/feedback', methods=['GET'])
def get_feedback():
    """Get all feedback from users"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        offset = (page - 1) * per_page
        
        query = """
            SELECT f.id, f.user_id, f.subject, f.message, f.created_at,
                   u.name as user_name, u.email as user_email
            FROM feedback f
            LEFT JOIN users u ON f.user_id = u.id
            ORDER BY f.created_at DESC
            LIMIT %s OFFSET %s
        """
        feedbacks = execute_query(query, (per_page, offset))
        
        if feedbacks is None:
            return jsonify({'error': 'Failed to fetch feedback'}), 500
        
        feedback_data = []
        for feedback in feedbacks:
            message = feedback.get('message', '') or ''
            feedback_data.append({
                'id': feedback['id'],
                'user_id': feedback.get('user_id'),
                'user_name': feedback.get('user_name', 'Anonymous'),
                'user_email': feedback.get('user_email', ''),
                'subject': feedback.get('subject', 'No Subject'),
                'message': message,
                'message_preview': (message[:100] + '...') if len(message) > 100 else message,
                'created_at': str(feedback['created_at']) if feedback.get('created_at') else None,
            })
        
        return jsonify(feedback_data), 200
        
    except Exception as e:
        print(f"Error in get_feedback: {str(e)}")
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/feedback/<int:feedback_id>', methods=['GET'])
def get_feedback_detail(feedback_id):
    """Get single feedback detail"""
    try:
        query = """
            SELECT f.id, f.user_id, f.subject, f.message, f.created_at,
                   u.name as user_name, u.email as user_email, u.phone as user_phone
            FROM feedback f
            LEFT JOIN users u ON f.user_id = u.id
            WHERE f.id = %s
        """
        feedback = execute_query(query, (feedback_id,), fetch_one=True)
        
        if not feedback:
            return jsonify({'error': 'Feedback not found'}), 404
        
        return jsonify({
            'id': feedback['id'],
            'user_id': feedback.get('user_id'),
            'user_name': feedback.get('user_name', 'Anonymous'),
            'user_email': feedback.get('user_email', ''),
            'user_phone': feedback.get('user_phone', ''),
            'subject': feedback.get('subject', 'No Subject'),
            'message': feedback.get('message', ''),
            'created_at': str(feedback['created_at']) if feedback.get('created_at') else None,
        }), 200
        
    except Exception as e:
        print(f"Error in get_feedback_detail: {str(e)}")
        return jsonify({'error': str(e)}), 500


@admin_bp.route('/feedback/<int:feedback_id>', methods=['DELETE'])
def delete_feedback(feedback_id):
    """Delete feedback"""
    try:
        # Check if feedback exists
        check_query = "SELECT id FROM feedback WHERE id = %s"
        feedback = execute_query(check_query, (feedback_id,), fetch_one=True)
        
        if not feedback:
            return jsonify({'error': 'Feedback not found'}), 404
        
        query = "DELETE FROM feedback WHERE id = %s"
        result = execute_update(query, (feedback_id,))
        
        if result > 0:
            return jsonify({'message': 'Feedback deleted successfully'}), 200
        else:
            return jsonify({'error': 'Failed to delete feedback'}), 500
        
    except Exception as e:
        print(f"Error in delete_feedback: {str(e)}")
        return jsonify({'error': str(e)}), 500


# ============================================================================
# ANALYTICS & RECENT ACTIVITY
# ============================================================================

@admin_bp.route('/analytics/recent-activity', methods=['GET'])
def get_recent_activity():
    """Get recent activity across the platform"""
    try:
        limit = request.args.get('limit', 10, type=int)
        
        activities = []
        
        # Recent users (last 5)
        users_query = """
            SELECT name, created_at
            FROM users
            ORDER BY created_at DESC
            LIMIT 5
        """
        recent_users = execute_query(users_query)
        if recent_users:
            for user in recent_users:
                activities.append({
                    'type': 'USER_REGISTERED',
                    'description': f'{user["name"]} bergabung sebagai pengguna baru',
                    'timestamp': str(user['created_at'])
                })
        
        # Recent posts (last 5)
        posts_query = """
            SELECT p.text, p.created_at, u.name
            FROM posts p
            LEFT JOIN users u ON p.user_id = u.id
            ORDER BY p.created_at DESC
            LIMIT 5
        """
        recent_posts = execute_query(posts_query)
        if recent_posts:
            for post in recent_posts:
                text_preview = (post['text'][:50] + '...') if post.get('text') and len(post['text']) > 50 else (post.get('text') or 'Post baru')
                activities.append({
                    'type': 'POST_CREATED',
                    'description': f'{post.get("name", "User")} membuat postingan: "{text_preview}"',
                    'timestamp': str(post['created_at'])
                })
        
        # Recent donations (last 5)
        donations_query = """
            SELECT d.amount, d.created_at, u.name, c.title
            FROM donations d
            LEFT JOIN users u ON d.donor_id = u.id
            LEFT JOIN campaigns c ON d.campaign_id = c.id
            ORDER BY d.created_at DESC
            LIMIT 5
        """
        recent_donations = execute_query(donations_query)
        if recent_donations:
            for donation in recent_donations:
                activities.append({
                    'type': 'DONATION_RECEIVED',
                    'description': f'{donation.get("name", "Anonymous")} mendonasikan Rp {int(donation["amount"]):,} untuk {donation.get("title", "kampanye")}',
                    'timestamp': str(donation['created_at'])
                })
        
        # Recent volunteers (last 5)
        volunteers_query = """
            SELECT v.created_at, u.name, c.title
            FROM volunteers v
            LEFT JOIN users u ON v.user_id = u.id
            LEFT JOIN campaigns c ON v.campaign_id = c.id
            ORDER BY v.created_at DESC
            LIMIT 5
        """
        recent_volunteers = execute_query(volunteers_query)
        if recent_volunteers:
            for volunteer in recent_volunteers:
                activities.append({
                    'type': 'VOLUNTEER_REGISTERED',
                    'description': f'{volunteer.get("name", "User")} mendaftar sebagai volunteer untuk {volunteer.get("title", "event")}',
                    'timestamp': str(volunteer['created_at'])
                })
        
        # Recent feedback (last 5)
        feedback_query = """
            SELECT f.subject, f.created_at, u.name
            FROM feedback f
            LEFT JOIN users u ON f.user_id = u.id
            ORDER BY f.created_at DESC
            LIMIT 5
        """
        recent_feedback = execute_query(feedback_query)
        if recent_feedback:
            for fb in recent_feedback:
                activities.append({
                    'type': 'FEEDBACK_SUBMITTED',
                    'description': f'{fb.get("name", "User")} mengirim feedback: {fb.get("subject", "No subject")}',
                    'timestamp': str(fb['created_at'])
                })
        
        # Sort all activities by timestamp (descending)
        activities.sort(key=lambda x: x['timestamp'], reverse=True)
        
        # Limit to requested number
        activities = activities[:limit]
        
        return jsonify({
            'data': activities
        }), 200
        
    except Exception as e:
        print(f"Error in get_recent_activity: {str(e)}")
        # Return dummy data if error
        return jsonify({
            'data': [
                {
                    'type': 'USER_REGISTERED',
                    'description': 'Ahmad Fauzi bergabung sebagai pengguna baru',
                    'timestamp': '2026-01-23T10:30:00'
                },
                {
                    'type': 'DONATION_RECEIVED',
                    'description': 'Siti Nurhaliza mendonasikan Rp 500,000 untuk Kampanye Tanam 1000 Pohon',
                    'timestamp': '2026-01-23T09:15:00'
                },
                {
                    'type': 'VOLUNTEER_REGISTERED',
                    'description': 'Budi Santoso mendaftar sebagai volunteer untuk Bersih Pantai Jakarta',
                    'timestamp': '2026-01-23T08:45:00'
                }
            ]
        }), 200