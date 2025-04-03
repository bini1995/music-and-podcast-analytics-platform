from flask import Flask, request, jsonify, session, render_template, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from flask_cors import CORS
import os
from flask_session import Session
from flask_migrate import Migrate
import redis
from datetime import timedelta
from functools import wraps
import re
from models import db, User, StreamingMetrics
from flask_talisman import Talisman

# Initialize Flask app
app = Flask(__name__)

# CORS Configuration
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

# Talisman Configuration (Remove force_https to avoid SSL errors)
Talisman(app, content_security_policy={
    "script-src": ["'self'", "https://cdn.plot.ly", "'unsafe-eval'"]
}, force_https=False)

# Application Configuration
app.config['SECRET_KEY'] = os.environ.get("SECRET_KEY", "supersecretkey")
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:TATA1tata1@localhost/music_analytics'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_PERMANENT'] = True
app.config['SESSION_USE_SIGNER'] = True
app.config['SESSION_KEY_PREFIX'] = 'session:'
app.config['SESSION_COOKIE_NAME'] = "music_analytics_session"
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = False  # Set to True in production
app.config['SESSION_REDIS'] = redis.StrictRedis(
    host='127.0.0.1', port=6379, db=0, decode_responses=False
)
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(days=7)

# Initialize Extensions
db.init_app(app)
bcrypt = Bcrypt(app)
server_session = Session(app)
migrate = Migrate(app, db)

# Set up Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Input Validation Functions
def is_valid_username(username):
    return bool(re.match(r'^[a-zA-Z0-9]{4,20}$', username))

def is_valid_password(password):
    return bool(re.match(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d).{8,}$', password))

# Authentication Routes
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    user = User.query.filter_by(username=username).first()
    if not user or not user.check_password(password):
        return jsonify({"error": "Invalid username or password"}), 401

    login_user(user, remember=True)
    return jsonify({"message": "Login successful!"})

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')

    if not is_valid_username(username) or not is_valid_password(password):
        return jsonify({"error": "Invalid input"}), 400

    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
    new_user = User(username=username, email=email, password_hash=hashed_password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logout successful"})

# RBAC Middleware
def role_required(required_role):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if current_user.role != required_role:
                return jsonify({"error": "Insufficient privileges"}), 403
            return f(*args, **kwargs)
        return wrapper
    return decorator

# Admin Dashboard Route
@app.route('/admin_dashboard', methods=['GET'])
@login_required
@role_required('admin')
def admin_dashboard():
    return jsonify({"message": "Welcome to the admin dashboard!"})

# Spotify Visualization Route
@app.route("/spotify/visuals", methods=["GET"])
def spotify_visuals():
    try:
        # Example data retrieval, modify as needed
        most_played_songs = [
            {"song": "Viva La Vida", "plays": 172},
            {"song": "Yellow", "plays": 180},
            {"song": "feelslikeimfallinginlove - Single Version", "plays": 148},
            {"song": "feelslikeimfallinginlove", "plays": 140},
            {"song": "Clocks", "plays": 168},
        ]

        # Aggregating artist play counts
        top_artists = [
            {"artist": "Coldplay", "plays": 172},
            {"artist": "Coldplay", "plays": 180},
            {"artist": "Coldplay", "plays": 148},
            {"artist": "Coldplay", "plays": 140},
            {"artist": "Coldplay", "plays": 168},
        ]

        # Aggregate artist plays
        artist_plays = {}
        for artist in top_artists:
            name = artist["artist"]
            plays = artist["plays"]
            if name in artist_plays:
                artist_plays[name] += plays
            else:
                artist_plays[name] = plays

        # Convert the aggregated data back into a list of dicts
        aggregated_artists = [{"artist": k, "plays": v} for k, v in artist_plays.items()]

        metrics = {
            "most_played_songs": most_played_songs,
            "top_artists": aggregated_artists,
        }

        return jsonify(metrics)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/")
def home():
    return render_template("dashboard.html")

# Static File Route
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

# Favicon Route
@app.route('/favicon.ico')
def favicon():
    return send_from_directory("static", "favicon.ico", mimetype="image/vnd.microsoft.icon")

# Run the app
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
