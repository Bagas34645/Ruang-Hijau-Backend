from flask import Blueprint, request, jsonify
from db import get_db

comment_bp = Blueprint("comment", __name__)


# GET COMMENTS FOR A POST
@comment_bp.route("/<int:post_id>", methods=["GET"])
def get_comments(post_id):
    """Get all comments for a specific post with pagination"""
    try:
        limit = int(request.args.get('limit', 10))
        page = int(request.args.get('page', 1))
        offset = (page - 1) * limit
        
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        # Verify post exists
        cursor.execute("SELECT id FROM posts WHERE id = %s", (post_id,))
        if not cursor.fetchone():
            cursor.close()
            db.close()
            return jsonify({
                "status": "error",
                "message": "Post not found"
            }), 404
        
        # Get total count
        cursor.execute("SELECT COUNT(*) as count FROM comments WHERE post_id = %s", (post_id,))
        total = cursor.fetchone()['count']
        
        # Get comments with user info
        cursor.execute("""
            SELECT c.id, c.post_id, c.user_id, u.name as author_name, u.profile_photo,
                   c.text, c.created_at
            FROM comments c
            JOIN users u ON c.user_id = u.id
            WHERE c.post_id = %s
            ORDER BY c.created_at DESC
            LIMIT %s OFFSET %s
        """, (post_id, limit, offset))
        
        comments = cursor.fetchall()
        cursor.close()
        db.close()
        
        return jsonify({
            "status": "success",
            "data": comments,
            "pagination": {
                "total": total,
                "page": page,
                "limit": limit,
                "pages": (total + limit - 1) // limit
            }
        }), 200
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to get comments: {str(e)}"
        }), 500


# CREATE COMMENT
@comment_bp.route("/", methods=["POST"])
def add_comment():
    """Add comment to a post"""
    try:
        data = request.json
        
        # Validate required fields
        post_id = data.get('post_id') if data else None
        user_id = data.get('user_id') if data else None
        text = data.get('text') if data else None
        
        if not post_id or not user_id or not text:
            return jsonify({
                "status": "error",
                "message": "post_id, user_id, and text are required"
            }), 400
        
        db = get_db()
        cursor = db.cursor()
        
        # Verify post exists
        cursor.execute("SELECT id FROM posts WHERE id = %s", (post_id,))
        if not cursor.fetchone():
            cursor.close()
            db.close()
            return jsonify({
                "status": "error",
                "message": "Post not found"
            }), 404
        
        # Verify user exists
        cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
        if not cursor.fetchone():
            cursor.close()
            db.close()
            return jsonify({
                "status": "error",
                "message": "User not found"
            }), 404
        
        cursor.execute("""
            INSERT INTO comments (post_id, user_id, text)
            VALUES (%s, %s, %s)
        """, (post_id, user_id, text))
        
        db.commit()
        comment_id = cursor.lastrowid
        cursor.close()
        db.close()
        
        return jsonify({
            "status": "success",
            "message": "Comment created successfully",
            "comment_id": comment_id
        }), 201
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to create comment: {str(e)}"
        }), 500


# UPDATE COMMENT
@comment_bp.route("/<int:comment_id>", methods=["PUT"])
def update_comment(comment_id):
    """Update comment text"""
    try:
        data = request.json
        
        if not data or not data.get('text'):
            return jsonify({
                "status": "error",
                "message": "Text is required"
            }), 400
        
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute("""
            UPDATE comments SET text = %s, updated_at = NOW()
            WHERE id = %s
        """, (data['text'], comment_id))
        
        if cursor.rowcount == 0:
            return jsonify({
                "status": "error",
                "message": "Comment not found"
            }), 404
        
        db.commit()
        cursor.close()
        db.close()
        
        return jsonify({
            "status": "success",
            "message": "Comment updated successfully"
        }), 200
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to update comment: {str(e)}"
        }), 500


# DELETE COMMENT
@comment_bp.route("/<int:comment_id>", methods=["DELETE"])
def delete_comment(comment_id):
    """Delete comment by ID"""
    try:
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute("DELETE FROM comments WHERE id = %s", (comment_id,))
        
        if cursor.rowcount == 0:
            return jsonify({
                "status": "error",
                "message": "Comment not found"
            }), 404
        
        db.commit()
        cursor.close()
        db.close()
        
        return jsonify({
            "status": "success",
            "message": "Comment deleted successfully"
        }), 200
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to delete comment: {str(e)}"
        }), 500
