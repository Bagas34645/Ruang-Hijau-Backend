from flask import Blueprint, request, jsonify
from db import get_db

volunteer_bp = Blueprint("volunteer", __name__)


# GET VOLUNTEERS FOR CAMPAIGN
@volunteer_bp.route("/campaign/<int:campaign_id>", methods=["GET"])
def get_campaign_volunteers(campaign_id):
    """Get all volunteers for a specific campaign"""
    try:
        status_filter = request.args.get('status', None)  # Optional: pending, approved, rejected
        limit = int(request.args.get('limit', 20))
        page = int(request.args.get('page', 1))
        offset = (page - 1) * limit
        
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        # Verify campaign exists
        cursor.execute("SELECT id FROM campaigns WHERE id = %s", (campaign_id,))
        if not cursor.fetchone():
            cursor.close()
            db.close()
            return jsonify({
                "status": "error",
                "message": "Campaign not found"
            }), 404
        
        # Build WHERE clause
        where_clause = "WHERE v.campaign_id = %s"
        params = [campaign_id]
        
        if status_filter:
            where_clause += " AND v.status = %s"
            params.append(status_filter)
        
        # Get total count
        cursor.execute(f"SELECT COUNT(*) as count FROM volunteers v {where_clause}", params)
        total = cursor.fetchone()['count']
        
        params.append(limit)
        params.append(offset)
        
        # Get volunteers with user info
        cursor.execute(f"""
            SELECT v.id, v.campaign_id, v.user_id, u.name, u.profile_photo, u.phone, u.email,
                   v.status, v.applied_at, v.responded_at
            FROM volunteers v
            JOIN users u ON v.user_id = u.id
            {where_clause}
            ORDER BY v.applied_at DESC
            LIMIT %s OFFSET %s
        """, params)
        
        volunteers = cursor.fetchall()
        cursor.close()
        db.close()
        
        return jsonify({
            "status": "success",
            "data": volunteers,
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
            "message": f"Failed to get volunteers: {str(e)}"
        }), 500


# APPLY AS VOLUNTEER
@volunteer_bp.route("/", methods=["POST"])
def apply_volunteer():
    """Apply as volunteer for a campaign"""
    try:
        data = request.json
        
        # Get required fields
        campaign_id = data.get('campaign_id') if data else None
        user_id = data.get('user_id') if data else None
        
        if not campaign_id or not user_id:
            return jsonify({
                "status": "error",
                "message": "campaign_id and user_id are required"
            }), 400
        
        db = get_db()
        cursor = db.cursor()
        
        # Verify campaign exists
        cursor.execute("SELECT id FROM campaigns WHERE id = %s", (campaign_id,))
        if not cursor.fetchone():
            cursor.close()
            db.close()
            return jsonify({
                "status": "error",
                "message": "Campaign not found"
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
        
        # Check if already applied
        cursor.execute("""
            SELECT id FROM volunteers WHERE campaign_id = %s AND user_id = %s
        """, (campaign_id, user_id))
        
        if cursor.fetchone():
            cursor.close()
            db.close()
            return jsonify({
                "status": "error",
                "message": "You already applied for this campaign"
            }), 400
        
        # Insert volunteer application
        cursor.execute("""
            INSERT INTO volunteers (campaign_id, user_id, status)
            VALUES (%s, %s, 'pending')
        """, (campaign_id, user_id))
        
        volunteer_id = cursor.lastrowid
        
        # Create notification for campaign creator
        cursor.execute("""
            SELECT creator_id FROM campaigns WHERE id = %s
        """, (campaign_id,))
        creator_result = cursor.fetchone()
        
        if creator_result:
            creator_id = creator_result[0]
            cursor.execute("SELECT name FROM users WHERE id = %s", (user_id,))
            user_result = cursor.fetchone()
            user_name = user_result[0] if user_result else "Unknown"
            
            notification_message = f"{user_name} applied as a volunteer for your campaign"
            cursor.execute("""
                INSERT INTO notifications (user_id, type, message, related_id, related_type)
                VALUES (%s, 'volunteer_application', %s, %s, 'volunteer')
            """, (creator_id, notification_message, volunteer_id))
        
        db.commit()
        cursor.close()
        db.close()
        
        return jsonify({
            "status": "success",
            "message": "Volunteer application submitted successfully",
            "volunteer_id": volunteer_id
        }), 201
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to apply as volunteer: {str(e)}"
        }), 500


# ACCEPT VOLUNTEER
@volunteer_bp.route("/<int:volunteer_id>/accept", methods=["PUT"])
def accept_volunteer(volunteer_id):
    """Accept volunteer application"""
    try:
        db = get_db()
        cursor = db.cursor()
        
        # Verify volunteer application exists
        cursor.execute("""
            SELECT user_id, campaign_id FROM volunteers WHERE id = %s AND status = 'pending'
        """, (volunteer_id,))
        
        volunteer = cursor.fetchone()
        if not volunteer:
            cursor.close()
            db.close()
            return jsonify({
                "status": "error",
                "message": "Volunteer application not found or not in pending status"
            }), 404
        
        user_id = volunteer[0]
        campaign_id = volunteer[1]
        
        # Update volunteer status
        cursor.execute("""
            UPDATE volunteers SET status = 'approved', responded_at = NOW()
            WHERE id = %s
        """, (volunteer_id,))
        
        # Create notification for volunteer
        cursor.execute("SELECT title FROM campaigns WHERE id = %s", (campaign_id,))
        campaign_result = cursor.fetchone()
        campaign_title = campaign_result[0] if campaign_result else "Campaign"
        
        notification_message = f"Your volunteer application for '{campaign_title}' was accepted"
        cursor.execute("""
            INSERT INTO notifications (user_id, type, message, related_id, related_type)
            VALUES (%s, 'volunteer_accepted', %s, %s, 'volunteer')
        """, (user_id, notification_message, volunteer_id))
        
        db.commit()
        cursor.close()
        db.close()
        
        return jsonify({
            "status": "success",
            "message": "Volunteer accepted successfully"
        }), 200
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to accept volunteer: {str(e)}"
        }), 500


# REJECT VOLUNTEER
@volunteer_bp.route("/<int:volunteer_id>/reject", methods=["PUT"])
def reject_volunteer(volunteer_id):
    """Reject volunteer application"""
    try:
        data = request.json
        rejection_reason = data.get('reason', '') if data else ''
        
        db = get_db()
        cursor = db.cursor()
        
        # Verify volunteer application exists
        cursor.execute("""
            SELECT user_id, campaign_id FROM volunteers WHERE id = %s AND status = 'pending'
        """, (volunteer_id,))
        
        volunteer = cursor.fetchone()
        if not volunteer:
            cursor.close()
            db.close()
            return jsonify({
                "status": "error",
                "message": "Volunteer application not found or not in pending status"
            }), 404
        
        user_id = volunteer[0]
        campaign_id = volunteer[1]
        
        # Update volunteer status
        cursor.execute("""
            UPDATE volunteers SET status = 'rejected', responded_at = NOW()
            WHERE id = %s
        """, (volunteer_id,))
        
        # Create notification for volunteer
        cursor.execute("SELECT title FROM campaigns WHERE id = %s", (campaign_id,))
        campaign_result = cursor.fetchone()
        campaign_title = campaign_result[0] if campaign_result else "Campaign"
        
        notification_message = f"Your volunteer application for '{campaign_title}' was declined"
        if rejection_reason:
            notification_message += f": {rejection_reason}"
        
        cursor.execute("""
            INSERT INTO notifications (user_id, type, message, related_id, related_type)
            VALUES (%s, 'volunteer_rejected', %s, %s, 'volunteer')
        """, (user_id, notification_message, volunteer_id))
        
        db.commit()
        cursor.close()
        db.close()
        
        return jsonify({
            "status": "success",
            "message": "Volunteer rejected successfully"
        }), 200
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to reject volunteer: {str(e)}"
        }), 500


# GET VOLUNTEER APPLICATIONS FOR CAMPAIGN CREATOR
@volunteer_bp.route("/campaign/<int:campaign_id>/pending", methods=["GET"])
def get_pending_applications(campaign_id):
    """Get all pending volunteer applications for a campaign"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        # Verify campaign exists
        cursor.execute("SELECT id FROM campaigns WHERE id = %s", (campaign_id,))
        if not cursor.fetchone():
            cursor.close()
            db.close()
            return jsonify({
                "status": "error",
                "message": "Campaign not found"
            }), 404
        
        # Get pending applications
        cursor.execute("""
            SELECT v.id, v.campaign_id, v.user_id, u.name, u.profile_photo, u.phone, u.email,
                   v.status, v.applied_at
            FROM volunteers v
            JOIN users u ON v.user_id = u.id
            WHERE v.campaign_id = %s AND v.status = 'pending'
            ORDER BY v.applied_at ASC
        """, (campaign_id,))
        
        applications = cursor.fetchall()
        cursor.close()
        db.close()
        
        return jsonify({
            "status": "success",
            "data": applications,
            "count": len(applications)
        }), 200
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to get pending applications: {str(e)}"
        }), 500


# GET USER VOLUNTEER STATUS
@volunteer_bp.route("/user/<int:user_id>", methods=["GET"])
def get_user_volunteers(user_id):
    """Get all volunteer applications for a user"""
    try:
        status_filter = request.args.get('status', None)
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
        
        # Build WHERE clause
        where_clause = "WHERE v.user_id = %s"
        params = [user_id]
        
        if status_filter:
            where_clause += " AND v.status = %s"
            params.append(status_filter)
        
        # Get total count
        cursor.execute(f"SELECT COUNT(*) as count FROM volunteers v {where_clause}", params)
        total = cursor.fetchone()['count']
        
        params.append(limit)
        params.append(offset)
        
        # Get volunteer applications
        cursor.execute(f"""
            SELECT v.id, v.campaign_id, c.title as campaign_title, c.location,
                   v.status, v.applied_at, v.responded_at
            FROM volunteers v
            JOIN campaigns c ON v.campaign_id = c.id
            {where_clause}
            ORDER BY v.applied_at DESC
            LIMIT %s OFFSET %s
        """, params)
        
        applications = cursor.fetchall()
        cursor.close()
        db.close()
        
        return jsonify({
            "status": "success",
            "data": applications,
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
            "message": f"Failed to get volunteer applications: {str(e)}"
        }), 500
