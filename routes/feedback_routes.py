from flask import Blueprint, request, jsonify
from db import get_db
from utils.sentiment_analyzer import analyze_feedback_sentiment
from datetime import datetime, timedelta
from collections import defaultdict

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


# FEEDBACK STATISTICS FOR ADMIN DASHBOARD
@feedback_bp.route("/stats", methods=["GET"])
def get_feedback_stats():
    """Get feedback statistics overview"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        # Total feedback count
        cursor.execute("SELECT COUNT(*) as total FROM feedback")
        total = cursor.fetchone()['total']
        
        # Average rating
        cursor.execute("SELECT AVG(rating) as avg_rating FROM feedback")
        avg_rating_result = cursor.fetchone()['avg_rating']
        avg_rating = float(avg_rating_result) if avg_rating_result else 0
        
        # Rating distribution
        cursor.execute("""
            SELECT rating, COUNT(*) as count 
            FROM feedback 
            GROUP BY rating 
            ORDER BY rating
        """)
        rating_distribution = {str(i): 0 for i in range(1, 6)}
        for row in cursor.fetchall():
            rating_distribution[str(row['rating'])] = row['count']
        
        # Category distribution
        cursor.execute("""
            SELECT category, COUNT(*) as count 
            FROM feedback 
            GROUP BY category
        """)
        category_distribution = {row['category']: row['count'] for row in cursor.fetchall()}
        
        # Feedback trend (last 30 days)
        cursor.execute("""
            SELECT DATE(created_at) as date, COUNT(*) as count
            FROM feedback 
            WHERE created_at >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
            GROUP BY DATE(created_at)
            ORDER BY date
        """)
        daily_trend = []
        for row in cursor.fetchall():
            daily_trend.append({
                'date': row['date'].isoformat() if row['date'] else None,
                'count': row['count']
            })
        
        # This week vs last week comparison
        cursor.execute("""
            SELECT COUNT(*) as count FROM feedback 
            WHERE created_at >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
        """)
        this_week = cursor.fetchone()['count']
        
        cursor.execute("""
            SELECT COUNT(*) as count FROM feedback 
            WHERE created_at >= DATE_SUB(CURDATE(), INTERVAL 14 DAY)
            AND created_at < DATE_SUB(CURDATE(), INTERVAL 7 DAY)
        """)
        last_week = cursor.fetchone()['count']
        
        cursor.close()
        db.close()
        
        return jsonify({
            "status": "success",
            "stats": {
                "total_feedback": total,
                "average_rating": round(avg_rating, 2),
                "rating_distribution": rating_distribution,
                "category_distribution": category_distribution,
                "daily_trend": daily_trend,
                "this_week": this_week,
                "last_week": last_week,
                "week_change": this_week - last_week
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to get feedback stats: {str(e)}"
        }), 500


# SENTIMENT ANALYSIS ENDPOINT
@feedback_bp.route("/analyze/<int:feedback_id>", methods=["GET"])
def analyze_single_feedback(feedback_id):
    """Analyze sentiment of a specific feedback"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT f.id, f.message, f.rating, f.category, f.created_at,
                   u.name as user_name
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
        
        # Analyze sentiment
        sentiment_result = analyze_feedback_sentiment(feedback['message'], feedback['rating'])
        
        return jsonify({
            "status": "success",
            "feedback": {
                "id": feedback['id'],
                "message": feedback['message'],
                "rating": feedback['rating'],
                "category": feedback['category'],
                "user_name": feedback['user_name'],
                "created_at": feedback['created_at'].isoformat() if feedback['created_at'] else None
            },
            "sentiment": sentiment_result
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to analyze feedback: {str(e)}"
        }), 500


# BULK SENTIMENT ANALYSIS
@feedback_bp.route("/sentiment/all", methods=["GET"])
def analyze_all_feedback():
    """Analyze sentiment of all feedback for dashboard"""
    try:
        limit = int(request.args.get('limit', 100))
        
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT f.id, f.message, f.rating, f.category, f.created_at,
                   u.name as user_name
            FROM feedback f
            JOIN users u ON f.user_id = u.id
            ORDER BY f.created_at DESC
            LIMIT %s
        """, (limit,))
        
        feedbacks = cursor.fetchall()
        cursor.close()
        db.close()
        
        # Analyze each feedback
        results = []
        sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
        total_confidence = 0
        
        for fb in feedbacks:
            sentiment = analyze_feedback_sentiment(fb['message'], fb['rating'])
            sentiment_counts[sentiment['sentiment']] += 1
            total_confidence += sentiment['confidence']
            
            results.append({
                'id': fb['id'],
                'message': fb['message'][:100] + '...' if len(fb['message']) > 100 else fb['message'],
                'rating': fb['rating'],
                'category': fb['category'],
                'user_name': fb['user_name'],
                'created_at': fb['created_at'].isoformat() if fb['created_at'] else None,
                'sentiment': sentiment['sentiment'],
                'confidence': sentiment['confidence'],
                'score': sentiment['score']
            })
        
        avg_confidence = total_confidence / len(results) if results else 0
        
        return jsonify({
            "status": "success",
            "summary": {
                "total_analyzed": len(results),
                "sentiment_distribution": sentiment_counts,
                "average_confidence": round(avg_confidence, 3),
                "positive_percentage": round(sentiment_counts['positive'] / len(results) * 100, 1) if results else 0,
                "negative_percentage": round(sentiment_counts['negative'] / len(results) * 100, 1) if results else 0,
                "neutral_percentage": round(sentiment_counts['neutral'] / len(results) * 100, 1) if results else 0
            },
            "feedbacks": results
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to analyze feedback: {str(e)}"
        }), 500


# SENTIMENT TREND OVER TIME
@feedback_bp.route("/sentiment/trend", methods=["GET"])
def get_sentiment_trend():
    """Get sentiment trend over time"""
    try:
        days = int(request.args.get('days', 30))
        
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT f.id, f.message, f.rating, DATE(f.created_at) as date
            FROM feedback f
            WHERE f.created_at >= DATE_SUB(CURDATE(), INTERVAL %s DAY)
            ORDER BY f.created_at
        """, (days,))
        
        feedbacks = cursor.fetchall()
        cursor.close()
        db.close()
        
        # Group by date and analyze sentiment
        daily_sentiment = defaultdict(lambda: {'positive': 0, 'negative': 0, 'neutral': 0, 'total': 0})
        
        for fb in feedbacks:
            sentiment = analyze_feedback_sentiment(fb['message'], fb['rating'])
            date_str = fb['date'].isoformat() if fb['date'] else 'unknown'
            daily_sentiment[date_str][sentiment['sentiment']] += 1
            daily_sentiment[date_str]['total'] += 1
        
        # Convert to list and calculate percentages
        trend_data = []
        for date, counts in sorted(daily_sentiment.items()):
            total = counts['total']
            trend_data.append({
                'date': date,
                'positive': counts['positive'],
                'negative': counts['negative'],
                'neutral': counts['neutral'],
                'total': total,
                'positive_pct': round(counts['positive'] / total * 100, 1) if total > 0 else 0,
                'negative_pct': round(counts['negative'] / total * 100, 1) if total > 0 else 0
            })
        
        return jsonify({
            "status": "success",
            "days": days,
            "trend": trend_data
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to get sentiment trend: {str(e)}"
        }), 500


# CATEGORY SENTIMENT ANALYSIS
@feedback_bp.route("/sentiment/by-category", methods=["GET"])
def get_sentiment_by_category():
    """Get sentiment analysis grouped by category"""
    try:
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT f.id, f.message, f.rating, f.category
            FROM feedback f
        """)
        
        feedbacks = cursor.fetchall()
        cursor.close()
        db.close()
        
        # Group by category and analyze sentiment
        category_sentiment = defaultdict(lambda: {
            'positive': 0, 'negative': 0, 'neutral': 0, 
            'total': 0, 'total_rating': 0
        })
        
        for fb in feedbacks:
            sentiment = analyze_feedback_sentiment(fb['message'], fb['rating'])
            category = fb['category'] or 'Lainnya'
            category_sentiment[category][sentiment['sentiment']] += 1
            category_sentiment[category]['total'] += 1
            category_sentiment[category]['total_rating'] += fb['rating']
        
        # Convert to list with statistics
        result = []
        for category, data in category_sentiment.items():
            total = data['total']
            result.append({
                'category': category,
                'total': total,
                'positive': data['positive'],
                'negative': data['negative'],
                'neutral': data['neutral'],
                'avg_rating': round(data['total_rating'] / total, 2) if total > 0 else 0,
                'positive_pct': round(data['positive'] / total * 100, 1) if total > 0 else 0,
                'negative_pct': round(data['negative'] / total * 100, 1) if total > 0 else 0,
                'sentiment_score': data['positive'] - data['negative']
            })
        
        # Sort by total feedback count
        result.sort(key=lambda x: x['total'], reverse=True)
        
        return jsonify({
            "status": "success",
            "categories": result
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to get category sentiment: {str(e)}"
        }), 500


# RECENT FEEDBACK WITH SENTIMENT
@feedback_bp.route("/recent", methods=["GET"])
def get_recent_feedback_with_sentiment():
    """Get recent feedback with sentiment analysis"""
    try:
        limit = int(request.args.get('limit', 10))
        
        db = get_db()
        cursor = db.cursor(dictionary=True)
        
        cursor.execute("""
            SELECT f.id, f.user_id, u.name as user_name, u.email as user_email,
                   f.category, f.rating, f.message, f.created_at
            FROM feedback f
            JOIN users u ON f.user_id = u.id
            ORDER BY f.created_at DESC
            LIMIT %s
        """, (limit,))
        
        feedbacks = cursor.fetchall()
        cursor.close()
        db.close()
        
        results = []
        for fb in feedbacks:
            sentiment = analyze_feedback_sentiment(fb['message'], fb['rating'])
            results.append({
                'id': fb['id'],
                'user_id': fb['user_id'],
                'user_name': fb['user_name'],
                'user_email': fb['user_email'],
                'category': fb['category'],
                'rating': fb['rating'],
                'message': fb['message'],
                'created_at': fb['created_at'].isoformat() if fb['created_at'] else None,
                'sentiment': sentiment['sentiment'],
                'sentiment_score': sentiment['score'],
                'confidence': sentiment['confidence']
            })
        
        return jsonify({
            "status": "success",
            "data": results
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Failed to get recent feedback: {str(e)}"
        }), 500
