from flask import Blueprint, request, jsonify
from db import get_db
from datetime import datetime

donation_bp = Blueprint("donation", __name__)


# CREATE DONATION
@donation_bp.route("/", methods=["POST"])
def create_donation():
    """
    Create new donation
    Required fields: campaign_id, donor_id, amount, payment_method, transaction_id
    Optional: is_anonymous (default false)
    """
    try:
        data = request.json
        
        # Get required fields
        campaign_id = data.get('campaign_id') if data else None
        donor_id = data.get('donor_id') if data else None
        amount = data.get('amount') if data else None
        payment_method = data.get('payment_method') if data else None
        transaction_id = data.get('transaction_id') if data else None
        is_anonymous = data.get('is_anonymous', False) if data else False
        
        # Validate required fields
        if not all([campaign_id, donor_id, amount, payment_method, transaction_id]):
            return jsonify({
                "status": "error",
                "message": "campaign_id, donor_id, amount, payment_method, and transaction_id are required"
            }), 400
        
        # Convert amount to float
        try:
            amount = float(amount)
            if amount <= 0:
                return jsonify({
                    "status": "error",
                    "message": "Amount must be greater than 0"
                }), 400
        except ValueError:
            return jsonify({
                "status": "error",
                "message": "Amount must be a valid number"
            }), 400
        
        db = get_db()
        cursor = db.cursor()
        
        # Verify campaign exists
        cursor.execute("SELECT id, current_amount, target_amount FROM campaigns WHERE id = %s", (campaign_id,))
        campaign = cursor.fetchone()
        
        if not campaign:
            cursor.close()
            db.close()
            return jsonify({
                "status": "error",
                "message": "Campaign not found"
            }), 404
        
        # Verify donor exists
        cursor.execute("SELECT id, name FROM users WHERE id = %s", (donor_id,))
        donor = cursor.fetchone()
        
        if not donor:
            cursor.close()
            db.close()
            return jsonify({
                "status": "error",
                "message": "Donor not found"
            }), 404
        
        # Check if transaction already exists
        cursor.execute("""
            SELECT id FROM donations WHERE transaction_id = %s
        """, (transaction_id,))
        
        if cursor.fetchone():
            cursor.close()
            db.close()
            return jsonify({
                "status": "error",
                "message": "Transaction already exists"
            }), 400
        
        # Insert donation
        cursor.execute("""
            INSERT INTO donations (campaign_id, donor_id, amount, payment_method, transaction_id, is_anonymous, donation_status)
            VALUES (%s, %s, %s, %s, %s, %s, 'completed')
        """, (campaign_id, donor_id, amount, payment_method, transaction_id, is_anonymous))
        
        donation_id = cursor.lastrowid
        
        # Update campaign current_amount
        new_current_amount = campaign[1] + amount
        cursor.execute("""
            UPDATE campaigns SET current_amount = %s WHERE id = %s
        """, (new_current_amount, campaign_id))
        
        # Create notification for campaign creator
        cursor.execute("""
            SELECT creator_id FROM campaigns WHERE id = %s
        """, (campaign_id,))
        creator_result = cursor.fetchone()
        
        if creator_result:
            creator_id = creator_result[0]
            donor_name = "Anonymous" if is_anonymous else donor[1]
            notification_message = f"{donor_name} donated Rp {amount:,.0f} to your campaign"
            
            cursor.execute("""
                INSERT INTO notifications (user_id, type, message, related_id, related_type)
                VALUES (%s, 'donation', %s, %s, 'campaign')
            """, (creator_id, notification_message, campaign_id))
        
        db.commit()
        cursor.close()
        db.close()
        
        return jsonify({
            "status": "success",
            "message": "Donation created successfully",
            "donation_id": donation_id,
            "campaign_progress": {
                "current": new_current_amount,
                "target": campaign[2],
                "percentage": (new_current_amount / campaign[2] * 100) if campaign[2] > 0 else 0
            }
        }), 201
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to create donation: {str(e)}"
        }), 500


# GET DONATIONS FOR CAMPAIGN
@donation_bp.route("/campaign/<int:campaign_id>", methods=["GET"])
def get_campaign_donations(campaign_id):
    """Get all donations for a specific campaign"""
    try:
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
        
        # Get total count
        cursor.execute("SELECT COUNT(*) as count FROM donations WHERE campaign_id = %s", (campaign_id,))
        total = cursor.fetchone()['count']
        
        # Get donations with donor info (anonymized if needed)
        cursor.execute("""
            SELECT d.id, d.campaign_id, d.donor_id, 
                   CASE WHEN d.is_anonymous THEN 'Anonymous' ELSE u.name END as donor_name,
                   d.amount, d.payment_method, d.donation_status as status, d.created_at
            FROM donations d
            LEFT JOIN users u ON d.donor_id = u.id
            WHERE d.campaign_id = %s
            ORDER BY d.created_at DESC
            LIMIT %s OFFSET %s
        """, (campaign_id, limit, offset))
        
        donations = cursor.fetchall()
        cursor.close()
        db.close()
        
        return jsonify({
            "status": "success",
            "data": donations,
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
            "message": f"Failed to get donations: {str(e)}"
        }), 500


# GET DONATIONS BY DONOR
@donation_bp.route("/donor/<int:donor_id>", methods=["GET"])
def get_donor_donations(donor_id):
    """Get all donations made by a specific donor"""
    try:
        limit = int(request.args.get('limit', 20))
        page = int(request.args.get('page', 1))
        offset = (page - 1) * limit
        
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        # Verify donor exists
        cursor.execute("SELECT id FROM users WHERE id = %s", (donor_id,))
        if not cursor.fetchone():
            cursor.close()
            db.close()
            return jsonify({
                "status": "error",
                "message": "Donor not found"
            }), 404
        
        # Get total count
        cursor.execute("SELECT COUNT(*) as count FROM donations WHERE donor_id = %s", (donor_id,))
        total = cursor.fetchone()['count']
        
        # Get donations with campaign info
        cursor.execute("""
            SELECT d.id, d.campaign_id, d.donor_id, c.title as campaign_title,
                   d.amount, d.payment_method, d.donation_status as status, d.created_at
            FROM donations d
            JOIN campaigns c ON d.campaign_id = c.id
            WHERE d.donor_id = %s
            ORDER BY d.created_at DESC
            LIMIT %s OFFSET %s
        """, (donor_id, limit, offset))
        
        donations = cursor.fetchall()
        cursor.close()
        db.close()
        
        return jsonify({
            "status": "success",
            "data": donations,
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
            "message": f"Failed to get donations: {str(e)}"
        }), 500


# GET SINGLE DONATION
@donation_bp.route("/<int:donation_id>", methods=["GET"])
def get_donation(donation_id):
    """Get details of a specific donation"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT d.id, d.campaign_id, c.title as campaign_title,
                   d.donor_id, CASE WHEN d.is_anonymous THEN 'Anonymous' ELSE u.name END as donor_name,
                   d.amount, d.payment_method, d.transaction_id, d.donation_status as status, d.created_at
            FROM donations d
            JOIN campaigns c ON d.campaign_id = c.id
            LEFT JOIN users u ON d.donor_id = u.id
            WHERE d.id = %s
        """, (donation_id,))
        
        donation = cursor.fetchone()
        cursor.close()
        db.close()
        
        if not donation:
            return jsonify({
                "status": "error",
                "message": "Donation not found"
            }), 404
        
        return jsonify({
            "status": "success",
            "data": donation
        }), 200
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to get donation: {str(e)}"
        }), 500


# GET DONATION STATISTICS
@donation_bp.route("/campaign/<int:campaign_id>/stats", methods=["GET"])
def get_campaign_donation_stats(campaign_id):
    """Get donation statistics for a campaign"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total_donations,
                SUM(amount) as total_amount,
                AVG(amount) as average_amount,
                MIN(amount) as min_amount,
                MAX(amount) as max_amount
            FROM donations
            WHERE campaign_id = %s AND donation_status = 'completed'
        """, (campaign_id,))
        
        stats = cursor.fetchone()
        
        # Get top payment methods
        cursor.execute("""
            SELECT payment_method, COUNT(*) as count
            FROM donations
            WHERE campaign_id = %s
            GROUP BY payment_method
            ORDER BY count DESC
        """, (campaign_id,))
        
        payment_methods = cursor.fetchall()
        cursor.close()
        db.close()
        
        return jsonify({
            "status": "success",
            "data": {
                "statistics": stats,
                "payment_methods": payment_methods
            }
        }), 200
    
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to get donation statistics: {str(e)}"
        }), 500
