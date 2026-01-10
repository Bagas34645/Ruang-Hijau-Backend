from flask import Blueprint, request, jsonify, current_app
import os
from werkzeug.utils import secure_filename
from db import get_db
import time

campaign_bp = Blueprint("campaign", __name__)

ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp'}


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def _ensure_uploads_dir():
    """Ensure uploads directory exists"""
    uploads = os.path.join(current_app.root_path, 'uploads')
    os.makedirs(uploads, exist_ok=True)
    return uploads


# GET ALL CAMPAIGNS
@campaign_bp.route("/", methods=["GET"])
def get_campaigns():
    """Get all active campaigns with pagination"""
    try:
        limit = int(request.args.get('limit', 20))
        page = int(request.args.get('page', 1))
        offset = (page - 1) * limit
        category = request.args.get('category', None)  # Optional filter
        
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        # Build WHERE clause
        where_clause = "WHERE c.campaign_status = 'active'"
        params = []
        
        if category:
            where_clause += " AND c.category = %s"
            params.append(category)
        
        # Get total count
        count_params = params.copy()
        cursor.execute(f"SELECT COUNT(*) as count FROM campaigns c {where_clause}", count_params)
        total = cursor.fetchone()['count']
        
        # Get campaigns with creator info and donation stats
        pagination_params = params.copy()
        pagination_params.append(limit)
        pagination_params.append(offset)
        
        cursor.execute(f"""
            SELECT c.id, c.creator_id, u.name as creator_name, u.profile_photo,
                   c.title, c.description, c.category, c.location, c.contact,
                   c.target_amount, c.current_amount, c.duration_days, 
                   c.need_volunteers, c.image, c.created_at,
                   (SELECT COUNT(*) FROM donations WHERE campaign_id = c.id) as donor_count,
                   (SELECT COUNT(*) FROM volunteers WHERE campaign_id = c.id AND volunteer_status = 'accepted') as volunteer_count
            FROM campaigns c
            JOIN users u ON c.creator_id = u.id
            {where_clause}
            ORDER BY c.created_at DESC
            LIMIT %s OFFSET %s
        """, pagination_params)
        
        campaigns = cursor.fetchall()
        cursor.close()
        db.close()
        
        return jsonify({
            "status": "success",
            "data": campaigns,
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
            "message": f"Failed to get campaigns: {str(e)}"
        }), 500


# GET CAMPAIGN BY ID
@campaign_bp.route("/<int:campaign_id>", methods=["GET"])
def get_campaign(campaign_id):
    """Get single campaign by ID with full details"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT c.id, c.creator_id, u.name as creator_name, u.profile_photo, u.phone as creator_phone,
                   c.title, c.description, c.category, c.location, c.contact,
                   c.target_amount, c.current_amount, c.duration_days, 
                   c.need_volunteers, c.image, c.campaign_status, c.created_at,
                   (SELECT COUNT(*) FROM donations WHERE campaign_id = c.id) as donor_count,
                   (SELECT COUNT(*) FROM volunteers WHERE campaign_id = c.id AND volunteer_status = 'accepted') as volunteer_count
            FROM campaigns c
            JOIN users u ON c.creator_id = u.id
            WHERE c.id = %s
        """, (campaign_id,))
        
        campaign = cursor.fetchone()
        cursor.close()
        db.close()
        
        if not campaign:
            return jsonify({
                "status": "error",
                "message": "Campaign not found"
            }), 404
        
        return jsonify({
            "status": "success",
            "data": campaign
        }), 200
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to get campaign: {str(e)}"
        }), 500


# CREATE CAMPAIGN
@campaign_bp.route("/", methods=["POST"])
def create_campaign():
    """
    Create new campaign
    Support both JSON and multipart/form-data
    Required fields: creator_id, title, description, target_amount, category, location, contact, duration_days
    Optional: need_volunteers (default false), image (file)
    """
    try:
        print("═══════════════════════════════════════════════════════")
        print("DEBUG: CREATE CAMPAIGN REQUEST")
        print("═══════════════════════════════════════════════════════")
        print(f"Content-Type: {request.content_type}")
        print(f"Is JSON: {request.is_json}")
        
        # Get data from either JSON or form
        if request.is_json:
            data = request.json
            creator_id = data.get('creator_id')
            title = data.get('title')
            description = data.get('description')
            target_amount = data.get('target_amount')
            category = data.get('category')
            location = data.get('location')
            contact = data.get('contact')
            duration_days = data.get('duration_days')
            need_volunteers = data.get('need_volunteers', False)
            image_filename = None
        else:
            creator_id = request.form.get('creator_id') or request.form.get('creatorId')
            title = request.form.get('title')
            description = request.form.get('description')
            target_amount = request.form.get('target_amount') or request.form.get('targetAmount')
            category = request.form.get('category')
            location = request.form.get('location')
            contact = request.form.get('contact')
            duration_days = request.form.get('duration_days') or request.form.get('durationDays')
            need_volunteers = request.form.get('need_volunteers', 'false').lower() == 'true'
            image_filename = None
            
            print(f"Form Data:")
            for key in request.form:
                print(f"  {key}: {request.form.get(key)}")
            
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
                    print(f"  Image saved: {filename}")
        
        print(f"Parsed Data:")
        print(f"  creator_id: {creator_id} (type: {type(creator_id).__name__})")
        print(f"  title: {title}")
        print(f"  description: {description[:50]}..." if description else "  description: None")
        print(f"  target_amount: {target_amount}")
        print(f"  category: {category}")
        print(f"  location: {location}")
        print(f"  contact: {contact}")
        print(f"  duration_days: {duration_days}")
        print(f"  need_volunteers: {need_volunteers}")
        print(f"  image_filename: {image_filename}")
        
        # Validate required fields
        if not all([creator_id, title, description, target_amount, category, location, contact, duration_days]):
            missing = []
            if not creator_id:
                missing.append('creator_id')
            if not title:
                missing.append('title')
            if not description:
                missing.append('description')
            if not target_amount:
                missing.append('target_amount')
            if not category:
                missing.append('category')
            if not location:
                missing.append('location')
            if not contact:
                missing.append('contact')
            if not duration_days:
                missing.append('duration_days')
            
            print(f"ERROR: Missing fields: {missing}")
            print("═══════════════════════════════════════════════════════")
            
            return jsonify({
                "status": "error",
                "message": f"Required fields missing: {', '.join(missing)}"
            }), 400
        
        # Convert numeric fields
        try:
            creator_id = int(creator_id)
            target_amount = float(target_amount)
            duration_days = int(duration_days)
        except ValueError as e:
            print(f"ERROR: Type conversion failed: {e}")
            print("═══════════════════════════════════════════════════════")
            return jsonify({
                "status": "error",
                "message": f"Invalid data types: creator_id must be integer, target_amount must be number, duration_days must be integer. Error: {str(e)}"
            }), 400
        
        db = get_db()
        cursor = db.cursor()
        
        # Verify creator exists
        cursor.execute("SELECT id FROM users WHERE id = %s", (creator_id,))
        user = cursor.fetchone()
        if not user:
            cursor.close()
            db.close()
            print(f"ERROR: Creator with id {creator_id} not found")
            print("═══════════════════════════════════════════════════════")
            return jsonify({
                "status": "error",
                "message": f"Creator with id {creator_id} not found"
            }), 404
        
        print(f"Creator found: {user}")
        
        cursor.execute("""
            INSERT INTO campaigns 
            (creator_id, title, description, target_amount, category, location, contact, duration_days, need_volunteers, image, campaign_status)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'active')
        """, (creator_id, title, description, target_amount, category, location, contact, duration_days, need_volunteers, image_filename))
        
        db.commit()
        campaign_id = cursor.lastrowid
        cursor.close()
        db.close()
        
        print(f"SUCCESS: Campaign created with id {campaign_id}")
        print("═══════════════════════════════════════════════════════")
        
        return jsonify({
            "status": "success",
            "message": "Campaign created successfully",
            "campaign_id": campaign_id
        }), 201
    
    except Exception as e:
        print(f"EXCEPTION: {str(e)}")
        print(f"Type: {type(e).__name__}")
        import traceback
        print(traceback.format_exc())
        print("═══════════════════════════════════════════════════════")
        return jsonify({
            "status": "error",
            "message": f"Failed to create campaign: {str(e)}"
        }), 500


# UPDATE CAMPAIGN
# UPDATE CAMPAIGN
@campaign_bp.route("/<int:campaign_id>", methods=["PUT"])
def update_campaign(campaign_id):
    """
    Update campaign details
    Support both JSON and multipart/form-data for image updates
    """
    try:
        print("═══════════════════════════════════════════════════════")
        print(f"DEBUG: UPDATE CAMPAIGN {campaign_id}")
        print("═══════════════════════════════════════════════════════")
        print(f"Content-Type: {request.content_type}")
        
        data = {}
        image_filename = None
        
        # Handle data source (JSON vs Form)
        if request.is_json:
            data = request.json
        else:
            # Handle Form Data
            data = request.form.to_dict()
            
            # Handle Image Upload
            if 'image' in request.files:
                file = request.files['image']
                if file and file.filename and allowed_file(file.filename):
                    uploads = _ensure_uploads_dir()
                    filename = f"{int(time.time())}_{secure_filename(file.filename)}"
                    save_path = os.path.join(uploads, filename)
                    file.save(save_path)
                    image_filename = filename
                    print(f"  New image saved: {filename}")

        if not data and not image_filename:
            return jsonify({
                "status": "error",
                "message": "No data to update"
            }), 400
        
        print(f"Update Data: {data}")
        
        db = get_db()
        cursor = db.cursor()
        
        # Verify campaign exists
        cursor.execute("SELECT * FROM campaigns WHERE id = %s", (campaign_id,))
        campaign = cursor.fetchone()
        
        if not campaign:
            cursor.close()
            db.close()
            return jsonify({
                "status": "error",
                "message": "Campaign not found"
            }), 404
            
        # Build dynamic UPDATE query
        allowed_fields = ['title', 'description', 'target_amount', 'category', 'location', 'contact', 'duration_days', 'need_volunteers', 'campaign_status']
        updates = []
        values = []
        
        for field in allowed_fields:
            if field in data:
                # Handle boolean conversion for need_volunteers
                value = data[field]
                if field == 'need_volunteers':
                     if isinstance(value, str):
                        value = value.lower() == 'true'
                
                updates.append(f"{field} = %s")
                values.append(value)
                
            elif field == 'campaign_status' and 'status' in data:
                updates.append("campaign_status = %s")
                values.append(data['status'])

        # Add image update if exists
        if image_filename:
            updates.append("image = %s")
            values.append(image_filename)
        
        if not updates:
            cursor.close()
            db.close()
            return jsonify({
                "status": "error",
                "message": "No valid fields to update"
            }), 400
        
        updates.append("updated_at = NOW()")
        values.append(campaign_id)
        
        query = f"UPDATE campaigns SET {', '.join(updates)} WHERE id = %s"
        cursor.execute(query, values)
        
        db.commit()
        cursor.close()
        db.close()
        
        return jsonify({
            "status": "success",
            "message": "Campaign updated successfully"
        }), 200
    
    except Exception as e:
        print(f"EXCEPTION: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return jsonify({
            "status": "error",
            "message": f"Failed to update campaign: {str(e)}"
        }), 500


# DELETE CAMPAIGN
@campaign_bp.route("/<int:campaign_id>", methods=["DELETE"])
def delete_campaign(campaign_id):
    """Delete campaign by ID"""
    try:
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute("DELETE FROM campaigns WHERE id = %s", (campaign_id,))
        
        if cursor.rowcount == 0:
            return jsonify({
                "status": "error",
                "message": "Campaign not found"
            }), 404
        
        db.commit()
        cursor.close()
        db.close()
        
        return jsonify({
            "status": "success",
            "message": "Campaign deleted successfully"
        }), 200
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to delete campaign: {str(e)}"
        }), 500
