from flask import Blueprint, request, jsonify, current_app
import os
from werkzeug.utils import secure_filename
from db import get_db
import time

post_bp = Blueprint("post", __name__)

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp'}


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def _ensure_uploads_dir():
    """Ensure uploads directory exists"""
    uploads = os.path.join(current_app.root_path, 'uploads')
    os.makedirs(uploads, exist_ok=True)
    return uploads


# GET ALL POSTS
@post_bp.route("/", methods=["GET"])
def get_posts():
    """
    Get all posts with pagination
    Query params: ?limit=20&page=1
    """
    try:
        limit = int(request.args.get('limit', 20))
        page = int(request.args.get('page', 1))
        offset = (page - 1) * limit
        
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        # Get total count
        cursor.execute("SELECT COUNT(*) as count FROM posts")
        total = cursor.fetchone()['count']
        
        # Get posts with user info
        cursor.execute("""
            SELECT p.id, p.user_id, u.name as author_name, u.profile_photo,
                   p.text, p.image, p.likes, p.created_at,
                   (SELECT COUNT(*) FROM comments WHERE post_id = p.id) as comment_count
            FROM posts p
            JOIN users u ON p.user_id = u.id
            ORDER BY p.created_at DESC
            LIMIT %s OFFSET %s
        """, (limit, offset))
        
        posts = cursor.fetchall()
        cursor.close()
        db.close()
        
        return jsonify({
            "status": "success",
            "data": posts,
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
            "message": f"Failed to get posts: {str(e)}"
        }), 500


# GET POST BY ID
@post_bp.route("/<int:post_id>", methods=["GET"])
def get_post(post_id):
    """Get single post by ID"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT p.id, p.user_id, u.name as author_name, u.profile_photo,
                   p.text, p.image, p.likes, p.created_at
            FROM posts p
            JOIN users u ON p.user_id = u.id
            WHERE p.id = %s
        """, (post_id,))
        
        post = cursor.fetchone()
        cursor.close()
        db.close()
        
        if not post:
            return jsonify({
                "status": "error",
                "message": "Post not found"
            }), 404
        
        return jsonify({
            "status": "success",
            "data": post
        }), 200
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to get post: {str(e)}"
        }), 500


# CREATE POST
@post_bp.route("/add", methods=["POST"])
def add_post():
    """
    Create new post
    Support both JSON and multipart/form-data
    JSON: {"user_id": 1, "text": "Post content"}
    Form: user_id, text, image (file)
    """
    try:
        # Get data from either JSON or form
        if request.is_json:
            data = request.json
            user_id = data.get('user_id')
            content = data.get('text') or data.get('content')
            image_filename = None
        else:
            user_id = request.form.get('user_id') or request.form.get('userId')
            content = request.form.get('text') or request.form.get('content')
            image_filename = None
            
            # Handle image upload
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename and allowed_file(file.filename):
                    try:
                        uploads = _ensure_uploads_dir()
                        # Generate unique filename with timestamp to avoid conflicts
                        filename = f"{int(time.time())}_{secure_filename(file.filename)}"
                        save_path = os.path.join(uploads, filename)
                        file.save(save_path)
                        image_filename = filename
                        print(f"DEBUG: Image saved successfully: {filename}")
                    except Exception as file_error:
                        print(f"DEBUG: Failed to save image: {str(file_error)}")
                        # Continue without image if save fails
                        image_filename = None
                else:
                    print(f"DEBUG: Image validation failed - file: {file}, filename: {file.filename if file else 'N/A'}")
        
        # Validate required fields
        if not user_id or not content:
            return jsonify({
                "status": "error",
                "message": "user_id and text are required"
            }), 400
        
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute("""
            INSERT INTO posts (user_id, text, image)
            VALUES (%s, %s, %s)
        """, (user_id, content, image_filename))
        
        db.commit()
        post_id = cursor.lastrowid
        cursor.close()
        db.close()
        
        print(f"DEBUG: Post created successfully - ID: {post_id}, Image: {image_filename}")
        
        return jsonify({
            "status": "success",
            "message": "Post created successfully",
            "post_id": post_id,
            "image": image_filename
        }), 201
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to create post: {str(e)}"
        }), 500


# UPDATE POST
@post_bp.route("/<int:post_id>", methods=["PUT"])
def update_post(post_id):
    """Update post content"""
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
            UPDATE posts SET text = %s, updated_at = NOW()
            WHERE id = %s
        """, (data['text'], post_id))
        
        if cursor.rowcount == 0:
            return jsonify({
                "status": "error",
                "message": "Post not found"
            }), 404
        
        db.commit()
        cursor.close()
        db.close()
        
        return jsonify({
            "status": "success",
            "message": "Post updated successfully"
        }), 200
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to update post: {str(e)}"
        }), 500


# DELETE POST
@post_bp.route("/<int:post_id>", methods=["DELETE"])
def delete_post(post_id):
    """Delete post by ID"""
    try:
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute("DELETE FROM posts WHERE id = %s", (post_id,))
        
        if cursor.rowcount == 0:
            return jsonify({
                "status": "error",
                "message": "Post not found"
            }), 404
        
        db.commit()
        cursor.close()
        db.close()
        
        return jsonify({
            "status": "success",
            "message": "Post deleted successfully"
        }), 200
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to delete post: {str(e)}"
        }), 500


# LIKE POST
@post_bp.route("/<int:post_id>/like", methods=["POST"])
def like_post(post_id):
    """Like/unlike a post"""
    try:
        data = request.json
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({
                "status": "error",
                "message": "user_id is required"
            }), 400
        
        db = get_db()
        cursor = db.cursor()
        
        # Check if already liked
        cursor.execute("""
            SELECT id FROM likes WHERE post_id = %s AND user_id = %s
        """, (post_id, user_id))
        
        if cursor.fetchone():
            # Unlike
            cursor.execute("""
                DELETE FROM likes WHERE post_id = %s AND user_id = %s
            """, (post_id, user_id))
            cursor.execute("""
                UPDATE posts SET likes = likes - 1 WHERE id = %s
            """, (post_id,))
            db.commit()
            cursor.close()
            db.close()
            
            return jsonify({
                "status": "success",
                "message": "Post unliked",
                "action": "unlike"
            }), 200
        else:
            # Like
            cursor.execute("""
                INSERT INTO likes (post_id, user_id) VALUES (%s, %s)
            """, (post_id, user_id))
            cursor.execute("""
                UPDATE posts SET likes = likes + 1 WHERE id = %s
            """, (post_id,))
            db.commit()
            cursor.close()
            db.close()
            
            return jsonify({
                "status": "success",
                "message": "Post liked",
                "action": "like"
            }), 200
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to like post: {str(e)}"
        }), 500


# GET POST LIKES
@post_bp.route("/<int:post_id>/likes", methods=["GET"])
def get_post_likes(post_id):
    """Get users who liked a post"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT u.id, u.name, u.profile_photo
            FROM likes l
            JOIN users u ON l.user_id = u.id
            WHERE l.post_id = %s
        """, (post_id,))
        
        likes = cursor.fetchall()
        cursor.close()
        db.close()
        
        return jsonify({
            "status": "success",
            "data": likes,
            "count": len(likes)
        }), 200
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to get likes: {str(e)}"
        }), 500

