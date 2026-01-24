from flask import Blueprint, request, jsonify, render_template, session, redirect, url_for
from db import get_db
from werkzeug.security import check_password_hash
from functools import wraps
from datetime import datetime, timedelta

admin_bp = Blueprint("admin", __name__)


# ROOT ADMIN ROUTE - Redirect to login or dashboard
@admin_bp.route("/", methods=["GET"])
def admin_root():
    """Redirect to login or dashboard based on auth status"""
    if 'admin_id' in session and session.get('admin_role') == 'admin':
        return redirect(url_for('admin.dashboard'))
    return redirect(url_for('admin.login'))


def admin_required(f):
    """Decorator to require admin authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session or 'admin_role' not in session:
            return redirect(url_for('admin.login'))
        if session.get('admin_role') != 'admin':
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_api_required(f):
    """Decorator to require admin authentication for API endpoints"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'admin_id' not in session or 'admin_role' not in session:
            return jsonify({
                "status": "error",
                "message": "Unauthorized"
            }), 401
        if session.get('admin_role') != 'admin':
            return jsonify({
                "status": "error",
                "message": "Forbidden"
            }), 403
        return f(*args, **kwargs)
    return decorated_function


# LOGIN PAGE
@admin_bp.route("/login", methods=["GET"])
def login():
    """Render login page"""
    if 'admin_id' in session and session.get('admin_role') == 'admin':
        return redirect(url_for('admin.dashboard'))
    return render_template('login.html')


# LOGIN HANDLER
@admin_bp.route("/login", methods=["POST"])
def login_post():
    """Handle login request"""
    try:
        data = request.json
        
        if not data or not data.get('email') or not data.get('password'):
            return jsonify({
                "status": "error",
                "message": "Email dan password harus diisi"
            }), 400
        
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        # Get user by email
        cursor.execute("""
            SELECT id, name, email, password, role 
            FROM users 
            WHERE email = %s
        """, (data['email'],))
        
        user = cursor.fetchone()
        cursor.close()
        db.close()
        
        if not user:
            return jsonify({
                "status": "error",
                "message": "Email atau password salah"
            }), 401
        
        # Check password
        if not check_password_hash(user['password'], data['password']):
            return jsonify({
                "status": "error",
                "message": "Email atau password salah"
            }), 401
        
        # Check if user is admin
        if user['role'] != 'admin':
            return jsonify({
                "status": "error",
                "message": "Akses ditolak. Hanya admin yang dapat masuk."
            }), 403
        
        # Set session
        session['admin_id'] = user['id']
        session['admin_name'] = user['name']
        session['admin_email'] = user['email']
        session['admin_role'] = user['role']
        session.permanent = True
        
        return jsonify({
            "status": "success",
            "message": "Login berhasil",
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
            "message": f"Login gagal: {str(e)}"
        }), 500


# CHECK AUTH
@admin_bp.route("/check-auth", methods=["GET"])
def check_auth():
    """Check if user is authenticated"""
    if 'admin_id' in session and session.get('admin_role') == 'admin':
        return jsonify({
            "status": "success",
            "user": {
                "id": session.get('admin_id'),
                "name": session.get('admin_name'),
                "email": session.get('admin_email'),
                "role": session.get('admin_role')
            }
        }), 200
    return jsonify({
        "status": "error",
        "message": "Not authenticated"
    }), 401


# LOGOUT
@admin_bp.route("/logout", methods=["POST"])
def logout():
    """Handle logout"""
    session.clear()
    return jsonify({
        "status": "success",
        "message": "Logout berhasil"
    }), 200


# DASHBOARD PAGE
@admin_bp.route("/dashboard", methods=["GET"])
@admin_required
def dashboard():
    """Render admin dashboard"""
    return render_template('admin_dashboard.html')


# STATS ENDPOINTS
@admin_bp.route("/stats/users", methods=["GET"])
@admin_api_required
def stats_users():
    """Get total users count"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT COUNT(*) as count FROM users")
        result = cursor.fetchone()
        cursor.close()
        db.close()
        
        return jsonify({
            "status": "success",
            "count": result['count']
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@admin_bp.route("/stats/posts", methods=["GET"])
@admin_api_required
def stats_posts():
    """Get total posts count"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT COUNT(*) as count FROM posts")
        result = cursor.fetchone()
        cursor.close()
        db.close()
        
        return jsonify({
            "status": "success",
            "count": result['count']
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@admin_bp.route("/stats/campaigns", methods=["GET"])
@admin_api_required
def stats_campaigns():
    """Get total campaigns count"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT COUNT(*) as count FROM campaigns")
        result = cursor.fetchone()
        cursor.close()
        db.close()
        
        return jsonify({
            "status": "success",
            "count": result['count']
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@admin_bp.route("/stats/donations", methods=["GET"])
@admin_api_required
def stats_donations():
    """Get total donations amount"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT COALESCE(SUM(amount), 0) as total FROM donations WHERE donation_status = 'completed'")
        result = cursor.fetchone()
        cursor.close()
        db.close()
        
        return jsonify({
            "status": "success",
            "total": float(result['total'])
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# RECENT ACTIVITY (legacy - kept for backward compatibility)
@admin_bp.route("/recent-activity-legacy", methods=["GET"])
@admin_api_required
def recent_activity():
    """Get recent activities"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        # Get recent users
        cursor.execute("""
            SELECT id, name, email, created_at, 'user' as type
            FROM users
            ORDER BY created_at DESC
            LIMIT 5
        """)
        users = cursor.fetchall()
        
        activities = []
        for user in users:
            activities.append({
                "type": "user",
                "title": f"Pengguna baru: {user['name']}",
                "created_at": user['created_at'].isoformat() if user['created_at'] else None
            })
        
        # Get recent posts
        cursor.execute("""
            SELECT p.id, p.text, p.created_at, u.name as user_name
            FROM posts p
            JOIN users u ON p.user_id = u.id
            ORDER BY p.created_at DESC
            LIMIT 5
        """)
        posts = cursor.fetchall()
        
        for post in posts:
            activities.append({
                "type": "post",
                "title": f"Postingan baru dari {post['user_name']}",
                "created_at": post['created_at'].isoformat() if post['created_at'] else None
            })
        
        # Sort by created_at descending
        activities.sort(key=lambda x: x['created_at'] or '', reverse=True)
        activities = activities[:10]  # Limit to 10 most recent
        
        cursor.close()
        db.close()
        
        return jsonify({
            "status": "success",
            "activities": activities
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# MONTHLY STATS (legacy - kept for backward compatibility)
@admin_bp.route("/monthly-stats-legacy", methods=["GET"])
@admin_api_required
def monthly_stats():
    """Get monthly statistics"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        # Get current month stats
        current_month = datetime.now().strftime('%Y-%m')
        
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM users
            WHERE DATE_FORMAT(created_at, '%Y-%m') = %s
        """, (current_month,))
        new_users = cursor.fetchone()['count']
        
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM posts
            WHERE DATE_FORMAT(created_at, '%Y-%m') = %s
        """, (current_month,))
        new_posts = cursor.fetchone()['count']
        
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM campaigns
            WHERE DATE_FORMAT(created_at, '%Y-%m') = %s
        """, (current_month,))
        new_campaigns = cursor.fetchone()['count']
        
        cursor.execute("""
            SELECT COALESCE(SUM(amount), 0) as total
            FROM donations
            WHERE DATE_FORMAT(created_at, '%Y-%m') = %s
            AND donation_status = 'completed'
        """, (current_month,))
        monthly_donations = cursor.fetchone()['total']
        
        cursor.close()
        db.close()
        
        return jsonify({
            "status": "success",
            "stats": {
                "Pengguna Baru": new_users,
                "Postingan Baru": new_posts,
                "Kampanye Baru": new_campaigns,
                "Donasi Bulan Ini": float(monthly_donations)
            }
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# USERS MANAGEMENT
@admin_bp.route("/users", methods=["GET"])
@admin_api_required
def get_users():
    """Get all users"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT id, name, email, role, created_at
            FROM users
            ORDER BY created_at DESC
            LIMIT 100
        """)
        
        users = cursor.fetchall()
        
        # Convert datetime to string
        for user in users:
            if user['created_at']:
                user['created_at'] = user['created_at'].isoformat()
        
        cursor.close()
        db.close()
        
        return jsonify({
            "status": "success",
            "users": users
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@admin_bp.route("/users/<int:user_id>", methods=["PATCH"])
@admin_api_required
def update_user(user_id):
    """Update user (currently: role)"""
    db = None
    cursor = None
    try:
        data = request.json or {}
        role = data.get("role")
        if role not in ("user", "admin"):
            return jsonify({"status": "error", "message": "role tidak valid"}), 400

        db = get_db()
        cursor = db.cursor()
        cursor.execute("UPDATE users SET role = %s, updated_at = NOW() WHERE id = %s", (role, user_id))
        db.commit()
        return jsonify({"status": "success", "message": "Role pengguna berhasil diupdate"}), 200
    except Exception as e:
        if db:
            db.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        try:
            if cursor:
                cursor.close()
        finally:
            if db:
                db.close()


@admin_bp.route("/users/<int:user_id>", methods=["DELETE"])
@admin_api_required
def delete_user(user_id):
    """Delete a user"""
    if session.get("admin_id") == user_id:
        return jsonify({"status": "error", "message": "Tidak bisa menghapus akun admin yang sedang login"}), 400

    db = None
    cursor = None
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        db.commit()
        return jsonify({"status": "success", "message": "Pengguna berhasil dihapus"}), 200
    except Exception as e:
        if db:
            db.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        try:
            if cursor:
                cursor.close()
        finally:
            if db:
                db.close()


# POSTS MANAGEMENT
@admin_bp.route("/posts", methods=["GET"])
@admin_api_required
def get_posts():
    """Get all posts"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT p.id, p.text, p.likes, p.created_at, u.name as user_name
            FROM posts p
            JOIN users u ON p.user_id = u.id
            ORDER BY p.created_at DESC
            LIMIT 100
        """)
        
        posts = cursor.fetchall()
        
        # Convert datetime to string
        for post in posts:
            if post['created_at']:
                post['created_at'] = post['created_at'].isoformat()
        
        cursor.close()
        db.close()
        
        return jsonify({
            "status": "success",
            "posts": posts
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@admin_bp.route("/posts/<int:post_id>", methods=["DELETE"])
@admin_api_required
def delete_post(post_id):
    """Delete a post"""
    try:
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute("DELETE FROM posts WHERE id = %s", (post_id,))
        db.commit()
        
        cursor.close()
        db.close()
        
        return jsonify({
            "status": "success",
            "message": "Postingan berhasil dihapus"
        }), 200
    except Exception as e:
        db.rollback()
        cursor.close()
        db.close()
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


# CAMPAIGNS MANAGEMENT
@admin_bp.route("/campaigns", methods=["GET"])
@admin_api_required
def get_campaigns():
    """Get all campaigns"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT c.id, c.title, c.category, c.target_amount, 
                   c.campaign_status, c.created_at,
                   COALESCE(SUM(d.amount), 0) as current_amount
            FROM campaigns c
            LEFT JOIN donations d ON c.id = d.campaign_id AND d.donation_status = 'completed'
            GROUP BY c.id
            ORDER BY c.created_at DESC
            LIMIT 100
        """)
        
        campaigns = cursor.fetchall()
        
        # Convert datetime and amounts
        for campaign in campaigns:
            if campaign['created_at']:
                campaign['created_at'] = campaign['created_at'].isoformat()
            campaign['current_amount'] = float(campaign['current_amount'])
            campaign['target_amount'] = float(campaign['target_amount'])
        
        cursor.close()
        db.close()
        
        return jsonify({
            "status": "success",
            "campaigns": campaigns
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@admin_bp.route("/campaigns/<int:campaign_id>", methods=["PATCH"])
@admin_api_required
def update_campaign(campaign_id):
    """Update campaign (currently: campaign_status)"""
    db = None
    cursor = None
    try:
        data = request.json or {}
        campaign_status = data.get("campaign_status")
        if campaign_status not in ("active", "completed", "cancelled"):
            return jsonify({"status": "error", "message": "campaign_status tidak valid"}), 400

        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            UPDATE campaigns
            SET campaign_status = %s, updated_at = NOW()
            WHERE id = %s
        """, (campaign_status, campaign_id))
        db.commit()
        return jsonify({"status": "success", "message": "Status kampanye berhasil diupdate"}), 200
    except Exception as e:
        if db:
            db.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        try:
            if cursor:
                cursor.close()
        finally:
            if db:
                db.close()


# DONATIONS MANAGEMENT
@admin_bp.route("/donations", methods=["GET"])
@admin_api_required
def get_donations():
    """Get all donations"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT d.id,
                   d.amount,
                   d.donation_status as status,
                   d.is_anonymous,
                   d.donor_name,
                   d.created_at,
                   COALESCE(u.name, d.donor_name, IF(d.is_anonymous, 'Anonim', 'Guest')) as user_name,
                   c.title as campaign_title
            FROM donations d
            LEFT JOIN users u ON d.donor_id = u.id
            JOIN campaigns c ON d.campaign_id = c.id
            ORDER BY d.created_at DESC
            LIMIT 100
        """)
        
        donations = cursor.fetchall()
        
        # Convert datetime and amounts
        for donation in donations:
            if donation['created_at']:
                donation['created_at'] = donation['created_at'].isoformat()
            donation['amount'] = float(donation['amount'])
        
        cursor.close()
        db.close()
        
        return jsonify({
            "status": "success",
            "donations": donations
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@admin_bp.route("/donations/<int:donation_id>", methods=["PATCH"])
@admin_api_required
def update_donation(donation_id):
    """Update donation (currently: donation_status)"""
    db = None
    cursor = None
    try:
        data = request.json or {}
        donation_status = data.get("donation_status")
        if donation_status not in ("pending", "completed", "failed", "refunded"):
            return jsonify({"status": "error", "message": "donation_status tidak valid"}), 400

        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            UPDATE donations
            SET donation_status = %s, updated_at = NOW()
            WHERE id = %s
        """, (donation_status, donation_id))
        db.commit()
        return jsonify({"status": "success", "message": "Status donasi berhasil diupdate"}), 200
    except Exception as e:
        if db:
            db.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        try:
            if cursor:
                cursor.close()
        finally:
            if db:
                db.close()


# ADDITIONAL STATS ENDPOINTS (based on ruang_hijau_database_fixed.sql)
@admin_bp.route("/stats/comments", methods=["GET"])
@admin_api_required
def stats_comments():
    """Get total comments count"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT COUNT(*) as count FROM comments")
        result = cursor.fetchone()
        cursor.close()
        db.close()
        return jsonify({"status": "success", "count": result["count"]}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@admin_bp.route("/stats/volunteers", methods=["GET"])
@admin_api_required
def stats_volunteers():
    """Get total volunteers count"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT COUNT(*) as count FROM volunteers")
        result = cursor.fetchone()
        cursor.close()
        db.close()
        return jsonify({"status": "success", "count": result["count"]}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@admin_bp.route("/stats/events", methods=["GET"])
@admin_api_required
def stats_events():
    """Get total events count"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT COUNT(*) as count FROM events")
        result = cursor.fetchone()
        cursor.close()
        db.close()
        return jsonify({"status": "success", "count": result["count"]}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@admin_bp.route("/stats/notifications-unread", methods=["GET"])
@admin_api_required
def stats_notifications_unread():
    """Get total unread notifications count"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT COUNT(*) as count FROM notifications WHERE is_read = FALSE")
        result = cursor.fetchone()
        cursor.close()
        db.close()
        return jsonify({"status": "success", "count": result["count"]}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# IMPROVED RECENT ACTIVITY (users, posts, donations, comments, volunteers, events)
@admin_bp.route("/recent-activity", methods=["GET"])
@admin_api_required
def recent_activity_v2():
    """Get recent activities (expanded)"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)

        activities = []

        # Recent users
        cursor.execute("""
            SELECT id, name, created_at
            FROM users
            ORDER BY created_at DESC
            LIMIT 5
        """)
        for u in cursor.fetchall():
            activities.append({
                "type": "user",
                "title": f"Pengguna baru: {u['name']}",
                "created_at": u["created_at"].isoformat() if u.get("created_at") else None
            })

        # Recent posts
        cursor.execute("""
            SELECT p.id, p.created_at, u.name as user_name
            FROM posts p
            JOIN users u ON p.user_id = u.id
            ORDER BY p.created_at DESC
            LIMIT 5
        """)
        for p in cursor.fetchall():
            activities.append({
                "type": "post",
                "title": f"Postingan baru dari {p['user_name']}",
                "created_at": p["created_at"].isoformat() if p.get("created_at") else None
            })

        # Recent donations (include anonymous)
        cursor.execute("""
            SELECT d.id, d.created_at,
                   COALESCE(u.name, d.donor_name, IF(d.is_anonymous, 'Anonim', 'Guest')) as donor_display,
                   c.title as campaign_title
            FROM donations d
            LEFT JOIN users u ON d.donor_id = u.id
            JOIN campaigns c ON d.campaign_id = c.id
            ORDER BY d.created_at DESC
            LIMIT 5
        """)
        for d in cursor.fetchall():
            activities.append({
                "type": "donation",
                "title": f"Donasi baru dari {d['donor_display']} untuk \"{d['campaign_title']}\"",
                "created_at": d["created_at"].isoformat() if d.get("created_at") else None
            })

        # Recent comments
        cursor.execute("""
            SELECT c.id, c.created_at, u.name as user_name
            FROM comments c
            JOIN users u ON c.user_id = u.id
            ORDER BY c.created_at DESC
            LIMIT 5
        """)
        for cmt in cursor.fetchall():
            activities.append({
                "type": "comment",
                "title": f"Komentar baru dari {cmt['user_name']}",
                "created_at": cmt["created_at"].isoformat() if cmt.get("created_at") else None
            })

        # Recent volunteers
        cursor.execute("""
            SELECT v.id, v.created_at, u.name as user_name, cp.title as campaign_title
            FROM volunteers v
            JOIN users u ON v.user_id = u.id
            JOIN campaigns cp ON v.campaign_id = cp.id
            ORDER BY v.created_at DESC
            LIMIT 5
        """)
        for v in cursor.fetchall():
            activities.append({
                "type": "volunteer",
                "title": f"Aplikasi relawan: {v['user_name']} ({v['campaign_title']})",
                "created_at": v["created_at"].isoformat() if v.get("created_at") else None
            })

        # Recent events
        cursor.execute("""
            SELECT e.id, e.created_at, e.title
            FROM events e
            ORDER BY e.created_at DESC
            LIMIT 5
        """)
        for ev in cursor.fetchall():
            activities.append({
                "type": "event",
                "title": f"Event baru: {ev['title']}",
                "created_at": ev["created_at"].isoformat() if ev.get("created_at") else None
            })

        activities.sort(key=lambda x: x["created_at"] or "", reverse=True)
        activities = activities[:10]

        cursor.close()
        db.close()
        return jsonify({"status": "success", "activities": activities}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# MONTHLY STATS (expanded)
@admin_bp.route("/monthly-stats", methods=["GET"])
@admin_api_required
def monthly_stats_v2():
    """Get monthly statistics (expanded)"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)

        current_month = datetime.now().strftime('%Y-%m')

        cursor.execute("""
            SELECT COUNT(*) as count
            FROM users
            WHERE DATE_FORMAT(created_at, '%Y-%m') = %s
        """, (current_month,))
        new_users = cursor.fetchone()["count"]

        cursor.execute("""
            SELECT COUNT(*) as count
            FROM posts
            WHERE DATE_FORMAT(created_at, '%Y-%m') = %s
        """, (current_month,))
        new_posts = cursor.fetchone()["count"]

        cursor.execute("""
            SELECT COUNT(*) as count
            FROM campaigns
            WHERE DATE_FORMAT(created_at, '%Y-%m') = %s
        """, (current_month,))
        new_campaigns = cursor.fetchone()["count"]

        cursor.execute("""
            SELECT COALESCE(SUM(amount), 0) as total
            FROM donations
            WHERE DATE_FORMAT(created_at, '%Y-%m') = %s
            AND donation_status = 'completed'
        """, (current_month,))
        monthly_donations = cursor.fetchone()["total"]

        cursor.execute("""
            SELECT COUNT(*) as count
            FROM comments
            WHERE DATE_FORMAT(created_at, '%Y-%m') = %s
        """, (current_month,))
        new_comments = cursor.fetchone()["count"]

        cursor.execute("""
            SELECT COUNT(*) as count
            FROM volunteers
            WHERE DATE_FORMAT(created_at, '%Y-%m') = %s
        """, (current_month,))
        new_volunteers = cursor.fetchone()["count"]

        cursor.execute("""
            SELECT COUNT(*) as count
            FROM events
            WHERE DATE_FORMAT(created_at, '%Y-%m') = %s
        """, (current_month,))
        new_events = cursor.fetchone()["count"]

        cursor.close()
        db.close()

        return jsonify({
            "status": "success",
            "stats": {
                "Pengguna Baru": new_users,
                "Postingan Baru": new_posts,
                "Kampanye Baru": new_campaigns,
                "Komentar Baru": new_comments,
                "Relawan Baru": new_volunteers,
                "Event Baru": new_events,
                "Donasi Bulan Ini": float(monthly_donations)
            }
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# COMMENTS MANAGEMENT
@admin_bp.route("/comments", methods=["GET"])
@admin_api_required
def get_comments():
    """Get all comments"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT c.id, c.post_id, c.text, c.created_at, u.name as user_name
            FROM comments c
            JOIN users u ON c.user_id = u.id
            ORDER BY c.created_at DESC
            LIMIT 100
        """)
        comments = cursor.fetchall()
        for c in comments:
            if c.get("created_at"):
                c["created_at"] = c["created_at"].isoformat()
        cursor.close()
        db.close()
        return jsonify({"status": "success", "comments": comments}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@admin_bp.route("/comments/<int:comment_id>", methods=["DELETE"])
@admin_api_required
def delete_comment(comment_id):
    """Delete a comment"""
    db = None
    cursor = None
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("DELETE FROM comments WHERE id = %s", (comment_id,))
        db.commit()
        return jsonify({"status": "success", "message": "Komentar berhasil dihapus"}), 200
    except Exception as e:
        if db:
            db.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        try:
            if cursor:
                cursor.close()
        finally:
            if db:
                db.close()


# VOLUNTEERS MANAGEMENT
@admin_bp.route("/volunteers", methods=["GET"])
@admin_api_required
def get_volunteers():
    """Get volunteers"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT v.id, v.volunteer_status, v.hours_contributed, v.created_at,
                   u.name as user_name,
                   c.title as campaign_title
            FROM volunteers v
            JOIN users u ON v.user_id = u.id
            JOIN campaigns c ON v.campaign_id = c.id
            ORDER BY v.created_at DESC
            LIMIT 100
        """)
        volunteers = cursor.fetchall()
        for v in volunteers:
            if v.get("created_at"):
                v["created_at"] = v["created_at"].isoformat()
            v["hours_contributed"] = float(v.get("hours_contributed") or 0)
        cursor.close()
        db.close()
        return jsonify({"status": "success", "volunteers": volunteers}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@admin_bp.route("/volunteers/<int:volunteer_id>", methods=["PATCH"])
@admin_api_required
def update_volunteer(volunteer_id):
    """Update volunteer status / hours"""
    db = None
    cursor = None
    try:
        data = request.json or {}
        volunteer_status = data.get("volunteer_status")
        hours_contributed = data.get("hours_contributed")

        if volunteer_status not in ("applied", "accepted", "rejected", "completed"):
            return jsonify({"status": "error", "message": "volunteer_status tidak valid"}), 400

        try:
            hours_val = float(hours_contributed)
            if hours_val < 0:
                raise ValueError()
        except Exception:
            return jsonify({"status": "error", "message": "hours_contributed tidak valid"}), 400

        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            UPDATE volunteers
            SET volunteer_status = %s, hours_contributed = %s, updated_at = NOW()
            WHERE id = %s
        """, (volunteer_status, hours_val, volunteer_id))
        db.commit()
        return jsonify({"status": "success", "message": "Relawan berhasil diupdate"}), 200
    except Exception as e:
        if db:
            db.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        try:
            if cursor:
                cursor.close()
        finally:
            if db:
                db.close()


# EVENTS MANAGEMENT
@admin_bp.route("/events", methods=["GET"])
@admin_api_required
def get_events():
    """Get events"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT e.id, e.title, e.description, e.date, e.location, e.event_status, e.created_at,
                   u.name as organizer_name
            FROM events e
            LEFT JOIN users u ON e.organizer_id = u.id
            ORDER BY e.date DESC
            LIMIT 100
        """)
        events = cursor.fetchall()
        for ev in events:
            if ev.get("date"):
                ev["date"] = ev["date"].isoformat()
            if ev.get("created_at"):
                ev["created_at"] = ev["created_at"].isoformat()
        cursor.close()
        db.close()
        return jsonify({"status": "success", "events": events}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@admin_bp.route("/events", methods=["POST"])
@admin_api_required
def create_event():
    """Create event"""
    db = None
    cursor = None
    try:
        data = request.json or {}
        title = (data.get("title") or "").strip()
        date_str = (data.get("date") or "").strip()
        description = data.get("description")
        location = data.get("location")
        event_status = data.get("event_status") or "upcoming"

        if not title or not date_str:
            return jsonify({"status": "error", "message": "title dan date wajib"}), 400
        if event_status not in ("upcoming", "ongoing", "completed", "cancelled"):
            return jsonify({"status": "error", "message": "event_status tidak valid"}), 400

        # MySQL DATETIME format expected: 'YYYY-MM-DD HH:MM:SS'
        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO events (title, description, date, location, organizer_id, event_status)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (title, description, date_str, location, session.get("admin_id"), event_status))
        db.commit()
        return jsonify({"status": "success", "message": "Event berhasil dibuat", "id": cursor.lastrowid}), 201
    except Exception as e:
        if db:
            db.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        try:
            if cursor:
                cursor.close()
        finally:
            if db:
                db.close()


@admin_bp.route("/events/<int:event_id>", methods=["GET"])
@admin_api_required
def get_event(event_id):
    """Get event by id"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT id, title, description, date, location, event_status
            FROM events
            WHERE id = %s
        """, (event_id,))
        ev = cursor.fetchone()
        cursor.close()
        db.close()
        if not ev:
            return jsonify({"status": "error", "message": "Event tidak ditemukan"}), 404
        # Provide both formatted and raw (for prompt default)
        if ev.get("date"):
            ev["date_raw"] = ev["date"].strftime("%Y-%m-%d %H:%M:%S")
            ev["date"] = ev["date"].isoformat()
        return jsonify({"status": "success", "event": ev}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@admin_bp.route("/events/<int:event_id>", methods=["PUT"])
@admin_api_required
def update_event(event_id):
    """Update event"""
    db = None
    cursor = None
    try:
        data = request.json or {}
        title = (data.get("title") or "").strip()
        date_str = (data.get("date") or "").strip()
        description = data.get("description")
        location = data.get("location")
        event_status = data.get("event_status") or "upcoming"

        if not title or not date_str:
            return jsonify({"status": "error", "message": "title dan date wajib"}), 400
        if event_status not in ("upcoming", "ongoing", "completed", "cancelled"):
            return jsonify({"status": "error", "message": "event_status tidak valid"}), 400

        db = get_db()
        cursor = db.cursor()
        cursor.execute("""
            UPDATE events
            SET title = %s,
                description = %s,
                date = %s,
                location = %s,
                event_status = %s,
                updated_at = NOW()
            WHERE id = %s
        """, (title, description, date_str, location, event_status, event_id))
        db.commit()
        return jsonify({"status": "success", "message": "Event berhasil diupdate"}), 200
    except Exception as e:
        if db:
            db.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        try:
            if cursor:
                cursor.close()
        finally:
            if db:
                db.close()


@admin_bp.route("/events/<int:event_id>", methods=["DELETE"])
@admin_api_required
def delete_event(event_id):
    """Delete event"""
    db = None
    cursor = None
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("DELETE FROM events WHERE id = %s", (event_id,))
        db.commit()
        return jsonify({"status": "success", "message": "Event berhasil dihapus"}), 200
    except Exception as e:
        if db:
            db.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        try:
            if cursor:
                cursor.close()
        finally:
            if db:
                db.close()


# NOTIFICATIONS MANAGEMENT
@admin_bp.route("/notifications", methods=["GET"])
@admin_api_required
def get_notifications():
    """Get notifications"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT n.id, n.title, n.notification_type, n.is_read, n.created_at,
                   u.name as user_name
            FROM notifications n
            JOIN users u ON n.user_id = u.id
            ORDER BY n.created_at DESC
            LIMIT 100
        """)
        notifications = cursor.fetchall()
        for n in notifications:
            if n.get("created_at"):
                n["created_at"] = n["created_at"].isoformat()
            n["is_read"] = bool(n.get("is_read"))
        cursor.close()
        db.close()
        return jsonify({"status": "success", "notifications": notifications}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@admin_bp.route("/notifications/<int:notification_id>", methods=["DELETE"])
@admin_api_required
def delete_notification(notification_id):
    """Delete notification"""
    db = None
    cursor = None
    try:
        db = get_db()
        cursor = db.cursor()
        cursor.execute("DELETE FROM notifications WHERE id = %s", (notification_id,))
        db.commit()
        return jsonify({"status": "success", "message": "Notifikasi berhasil dihapus"}), 200
    except Exception as e:
        if db:
            db.rollback()
        return jsonify({"status": "error", "message": str(e)}), 500
    finally:
        try:
            if cursor:
                cursor.close()
        finally:
            if db:
                db.close()


# LIKES ANALYTICS
@admin_bp.route("/likes/top-posts", methods=["GET"])
@admin_api_required
def top_liked_posts():
    """Get top liked posts based on likes table"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT p.id as post_id,
                   u.name as user_name,
                   LEFT(COALESCE(p.text, ''), 120) as text,
                   COUNT(l.id) as likes_count
            FROM posts p
            JOIN users u ON p.user_id = u.id
            LEFT JOIN likes l ON l.post_id = p.id
            GROUP BY p.id
            ORDER BY likes_count DESC, p.created_at DESC
            LIMIT 50
        """)
        posts = cursor.fetchall()
        for p in posts:
            p["likes_count"] = int(p.get("likes_count") or 0)
        cursor.close()
        db.close()
        return jsonify({"status": "success", "posts": posts}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
