from flask import Blueprint, request, jsonify
from db import get_db

feedback_bp = Blueprint("feedback", __name__)

def _serialize_feedback_row(row: dict) -> dict:
    """Ensure JSON-safe values (e.g., datetime -> string)."""
    if not row:
        return row
    out = dict(row)
    for k in ("created_at", "updated_at"):
        v = out.get(k)
        if hasattr(v, "isoformat"):
            out[k] = v.isoformat(sep=" ", timespec="seconds")
    return out


# CREATE FEEDBACK
@feedback_bp.route("/", methods=["POST"])
def submit_feedback():
    """Submit feedback from user"""
    try:
        data = request.json
        
        # Validate required fields
        user_id = data.get('user_id') if data else None
        category = data.get('category') if data else None
        rating = data.get('rating') if data else None
        message = data.get('message') if data else None
        
        if not user_id or not category or not rating or not message:
            return jsonify({
                "status": "error",
                "message": "user_id, category, rating, and message are required"
            }), 400
        
        # Validate rating range
        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                return jsonify({
                    "status": "error",
                    "message": "Rating must be between 1 and 5"
                }), 400
        except (ValueError, TypeError):
            return jsonify({
                "status": "error",
                "message": "Rating must be a valid integer"
            }), 400
        
        # Validate message length
        if len(message.strip()) < 10:
            return jsonify({
                "status": "error",
                "message": "Message must be at least 10 characters"
            }), 400
        
        db = get_db()
        cursor = db.cursor()
        
        # Verify user exists
        cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
        if not cursor.fetchone():
            cursor.close()
            db.close()
            return jsonify({
                "status": "error",
                "message": "User not found"
            }), 404
        
        # Insert feedback
        cursor.execute("""
            INSERT INTO feedback (user_id, category, rating, message)
            VALUES (%s, %s, %s, %s)
        """, (user_id, category, rating, message.strip()))
        
        db.commit()
        feedback_id = cursor.lastrowid
        
        # Fetch the created feedback with user info
        cursor.close()
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT f.id, f.user_id, u.name as user_name, u.email as user_email,
                   f.category, f.rating, f.message, f.created_at, f.updated_at
            FROM feedback f
            JOIN users u ON f.user_id = u.id
            WHERE f.id = %s
        """, (feedback_id,))
        created = cursor.fetchone()
        cursor.close()
        db.close()

        return jsonify({
            "status": "success",
            "message": "Feedback submitted successfully",
            "feedback_id": feedback_id,
            "data": _serialize_feedback_row(created) if created else None
        }), 201
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to submit feedback: {str(e)}"
        }), 500


# GET ALL FEEDBACK (for admin)
@feedback_bp.route("/", methods=["GET"])
def get_all_feedback():
    """Get all feedback with pagination (admin only)"""
    try:
        limit = int(request.args.get('limit', 20))
        page = int(request.args.get('page', 1))
        offset = (page - 1) * limit
        
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        # Get total count
        cursor.execute("SELECT COUNT(*) as count FROM feedback")
        total = cursor.fetchone()['count']
        
        # Get feedback with user info
        cursor.execute("""
            SELECT f.id, f.user_id, u.name as user_name, u.email as user_email,
                   f.category, f.rating, f.message, f.created_at, f.updated_at
            FROM feedback f
            JOIN users u ON f.user_id = u.id
            ORDER BY f.created_at DESC
            LIMIT %s OFFSET %s
        """, (limit, offset))
        
        feedback_list = cursor.fetchall()
        feedback_list = [_serialize_feedback_row(f) for f in feedback_list]
        cursor.close()
        db.close()
        
        return jsonify({
            "status": "success",
            "data": feedback_list,
            "pagination": {
                "total": total,
                "page": page,
                "limit": limit,
                "pages": (total + limit - 1) // limit if limit > 0 else 0
            }
        }), 200
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to get feedback: {str(e)}"
        }), 500


# GET FEEDBACK BY USER ID
@feedback_bp.route("/user/<int:user_id>", methods=["GET"])
def get_user_feedback(user_id):
    """Get all feedback from a specific user"""
    try:
        limit = int(request.args.get('limit', 20))
        page = int(request.args.get('page', 1))
        offset = (page - 1) * limit
        
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        # Verify user exists
        cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
        if not cursor.fetchone():
            cursor.close()
            db.close()
            return jsonify({
                "status": "error",
                "message": "User not found"
            }), 404
        
        # Get total count
        cursor.execute("SELECT COUNT(*) as count FROM feedback WHERE user_id = %s", (user_id,))
        total = cursor.fetchone()['count']
        
        # Get feedback with user info
        cursor.execute("""
            SELECT f.id, f.user_id, u.name as user_name, u.email as user_email,
                   f.category, f.rating, f.message, f.created_at, f.updated_at
            FROM feedback f
            JOIN users u ON f.user_id = u.id
            WHERE f.user_id = %s
            ORDER BY f.created_at DESC
            LIMIT %s OFFSET %s
        """, (user_id, limit, offset))
        
        feedback_list = cursor.fetchall()
        feedback_list = [_serialize_feedback_row(f) for f in feedback_list]
        cursor.close()
        db.close()
        
        return jsonify({
            "status": "success",
            "data": feedback_list,
            "pagination": {
                "total": total,
                "page": page,
                "limit": limit,
                "pages": (total + limit - 1) // limit if limit > 0 else 0
            }
        }), 200
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to get user feedback: {str(e)}"
        }), 500


# GET FEEDBACK BY ID
@feedback_bp.route("/<int:feedback_id>", methods=["GET"])
def get_feedback_by_id(feedback_id):
    """Get specific feedback by ID"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT f.id, f.user_id, u.name as user_name, u.email as user_email,
                   f.category, f.rating, f.message, f.created_at, f.updated_at
            FROM feedback f
            JOIN users u ON f.user_id = u.id
            WHERE f.id = %s
        """, (feedback_id,))
        
        feedback = cursor.fetchone()
        cursor.close()
        db.close()
        
        if not feedback:
            return jsonify({
                "status": "error",
                "message": "Feedback not found"
            }), 404
        
        return jsonify({
            "status": "success",
            "data": _serialize_feedback_row(feedback)
        }), 200
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to get feedback: {str(e)}"
        }), 500
