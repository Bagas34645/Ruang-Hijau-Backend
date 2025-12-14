from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Import routes
from routes.auth_routes import auth_bp
from routes.event_routes import event_bp
from routes.post_routes import post_bp
from routes.comment_routes import comment_bp

from flask import send_from_directory, current_app

# Register Blueprint
app.register_blueprint(auth_bp)
app.register_blueprint(event_bp)
app.register_blueprint(post_bp)
app.register_blueprint(comment_bp)


@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    # Serve files from the uploads directory inside the app root
    return send_from_directory(app.root_path + '/uploads', filename)

@app.route("/")
def index():
    return {"message": "Ruanghijau API Running"}

if __name__ == "__main__":
    app.run(debug=True)
