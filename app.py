from flask import Flask, send_from_directory, current_app, jsonify
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')

# Enable CORS with credentials
CORS(app, resources={
    r"/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"],
        "supports_credentials": True
    }
})

# Ensure uploads directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Import routes
from routes.auth_routes import auth_bp
from routes.event_routes import event_bp
from routes.post_routes import post_bp
from routes.comment_routes import comment_bp
from routes.campaign_routes import campaign_bp
from routes.donation_routes import donation_bp
from routes.volunteer_routes import volunteer_bp

# Register Blueprints
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(post_bp, url_prefix='/api/posts')
app.register_blueprint(comment_bp, url_prefix='/api/comments')
app.register_blueprint(event_bp, url_prefix='/api/events')
app.register_blueprint(campaign_bp, url_prefix='/api/campaigns')
app.register_blueprint(donation_bp, url_prefix='/api/donations')
app.register_blueprint(volunteer_bp, url_prefix='/api/volunteers')


@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    """Serve uploaded files with CORS headers"""
    try:
        response = send_from_directory(app.config['UPLOAD_FOLDER'], filename)
        # Ensure CORS headers are set
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response
    except Exception as e:
        print(f"DEBUG: Error serving file {filename}: {str(e)}")
        return jsonify({
            "error": "File not found",
            "filename": filename,
            "message": str(e)
        }), 404


@app.route('/uploads/<path:filename>', methods=['OPTIONS'])
def handle_uploads_options(filename):
    """Handle OPTIONS request for uploads"""
    response = jsonify({'status': 'ok'})
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response, 200


@app.route("/api")
@app.route("/api/")
def api_index():
    """API Information"""
    return jsonify({
        "message": "Ruang Hijau API v1.0",
        "status": "running",
        "endpoints": {
            "auth": "/api/auth",
            "posts": "/api/posts",
            "comments": "/api/comments",
            "events": "/api/events",
            "campaigns": "/api/campaigns",
            "donations": "/api/donations",
            "volunteers": "/api/volunteers"
        }
    }), 200


@app.route("/")
def index():
    """Root endpoint"""
    return jsonify({
        "message": "Ruang Hijau Backend API",
        "version": "1.0",
        "docs": "/api"
    }), 200


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({"error": "Endpoint not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({"error": "Internal server error", "message": str(error)}), 500


@app.errorhandler(400)
def bad_request(error):
    """Handle 400 errors"""
    return jsonify({"error": "Bad request"}), 400


if __name__ == "__main__":
    app.run(
        host=os.getenv('SERVER_HOST', '127.0.0.1'),
        port=int(os.getenv('SERVER_PORT', 5000)),
        debug=os.getenv('FLASK_DEBUG', True)
    )
