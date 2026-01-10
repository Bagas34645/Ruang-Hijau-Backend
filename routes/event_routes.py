from flask import Blueprint, request, jsonify, current_app
import os
from werkzeug.utils import secure_filename
from db import get_db
import time

event_bp = Blueprint("event", __name__)

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp'}


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def _ensure_uploads_dir():
    """Ensure uploads directory exists"""
    uploads = os.path.join(current_app.root_path, 'uploads')
    os.makedirs(uploads, exist_ok=True)
    return uploads


# GET ALL EVENTS
@event_bp.route("/", methods=["GET"])
def get_events():
    """Get all events with pagination"""
    try:
        limit = int(request.args.get('limit', 20))
        page = int(request.args.get('page', 1))
        offset = (page - 1) * limit
        
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        # Get total count
        cursor.execute("SELECT COUNT(*) as count FROM events")
        total = cursor.fetchone()['count']
        
        # Get events with organizer info
        cursor.execute("""
            SELECT e.id, e.title, e.description, e.date, e.location, 
                   e.image, e.created_at,
                   u.id as organizer_id, u.name as organizer_name
            FROM events e
            JOIN users u ON e.organizer_id = u.id
            ORDER BY e.date DESC
            LIMIT %s OFFSET %s
        """, (limit, offset))
        
        events = cursor.fetchall()
        cursor.close()
        db.close()
        
        return jsonify({
            "status": "success",
            "data": events,
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
            "message": f"Failed to get events: {str(e)}"
        }), 500


# GET EVENT BY ID
@event_bp.route("/<int:event_id>", methods=["GET"])
def get_event(event_id):
    """Get single event by ID"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT e.id, e.title, e.description, e.date, e.location, 
                   e.image, e.created_at,
                   u.id as organizer_id, u.name as organizer_name
            FROM events e
            JOIN users u ON e.organizer_id = u.id
            WHERE e.id = %s
        """, (event_id,))
        
        event = cursor.fetchone()
        cursor.close()
        db.close()
        
        if not event:
            return jsonify({
                "status": "error",
                "message": "Event not found"
            }), 404
        
        return jsonify({
            "status": "success",
            "data": event
        }), 200
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to get event: {str(e)}"
        }), 500


# CREATE EVENT
@event_bp.route("/", methods=["POST"])
def add_event():
    """
    Create new event
    Support both JSON and multipart/form-data
    JSON: {"organizer_id": 1, "title": "Event", "description": "Desc", "date": "2024-12-25", "location": "Jakarta"}
    Form: organizer_id, title, description, date, location, image (file)
    """
    try:
        # Get data from either JSON or form
        if request.is_json:
            data = request.json
            organizer_id = data.get('organizer_id')
            title = data.get('title')
            description = data.get('description')
            date = data.get('date')
            location = data.get('location')
            image_filename = None
        else:
            organizer_id = request.form.get('organizer_id') or request.form.get('organizerId')
            title = request.form.get('title')
            description = request.form.get('description')
            date = request.form.get('date')
            location = request.form.get('location')
            image_filename = None
            
            # Handle image upload
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename and allowed_file(file.filename):
                    uploads = _ensure_uploads_dir()
                    # Generate unique filename
                    filename = f"{int(time.time())}_{secure_filename(file.filename)}"
                    save_path = os.path.join(uploads, filename)
                    file.save(save_path)
                    image_filename = filename
        
        # Validate required fields
        if not organizer_id or not title or not description or not date or not location:
            return jsonify({
                "status": "error",
                "message": "organizer_id, title, description, date, and location are required"
            }), 400
        
        db = get_db()
        cursor = db.cursor()
        
        # Verify organizer exists
        cursor.execute("SELECT id FROM users WHERE id = %s", (organizer_id,))
        if not cursor.fetchone():
            cursor.close()
            db.close()
            return jsonify({
                "status": "error",
                "message": "Organizer not found"
            }), 404
        
        cursor.execute("""
            INSERT INTO events (organizer_id, title, description, date, location, image)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (organizer_id, title, description, date, location, image_filename))
        
        db.commit()
        event_id = cursor.lastrowid
        cursor.close()
        db.close()
        
        return jsonify({
            "status": "success",
            "message": "Event created successfully",
            "event_id": event_id
        }), 201
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to create event: {str(e)}"
        }), 500


# UPDATE EVENT
@event_bp.route("/<int:event_id>", methods=["PUT"])
def update_event(event_id):
    """Update event details"""
    try:
        data = request.json
        
        # At least one field must be provided
        if not data:
            return jsonify({
                "status": "error",
                "message": "No data to update"
            }), 400
        
        db = get_db()
        cursor = db.cursor()
        
        # Build dynamic UPDATE query
        allowed_fields = ['title', 'description', 'date', 'location']
        updates = []
        values = []
        
        for field in allowed_fields:
            if field in data:
                updates.append(f"{field} = %s")
                values.append(data[field])
        
        if not updates:
            cursor.close()
            db.close()
            return jsonify({
                "status": "error",
                "message": "No valid fields to update"
            }), 400
        
        updates.append("updated_at = NOW()")
        values.append(event_id)
        
        query = f"UPDATE events SET {', '.join(updates)} WHERE id = %s"
        cursor.execute(query, values)
        
        if cursor.rowcount == 0:
            db.close()
            return jsonify({
                "status": "error",
                "message": "Event not found"
            }), 404
        
        db.commit()
        cursor.close()
        db.close()
        
        return jsonify({
            "status": "success",
            "message": "Event updated successfully"
        }), 200
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to update event: {str(e)}"
        }), 500


# DELETE EVENT
@event_bp.route("/<int:event_id>", methods=["DELETE"])
def delete_event(event_id):
    """Delete event by ID"""
    try:
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute("DELETE FROM events WHERE id = %s", (event_id,))
        
        if cursor.rowcount == 0:
            return jsonify({
                "status": "error",
                "message": "Event not found"
            }), 404
        
        db.commit()
        cursor.close()
        db.close()
        
        return jsonify({
            "status": "success",
            "message": "Event deleted successfully"
        }), 200
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to delete event: {str(e)}"
        }), 500
