# app.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_session import Session
from flask_migrate import Migrate
from flask_cors import CORS
from flask_talisman import Talisman
import redis
import os
from datetime import timedelta

# Models & extensions
from models import db, User
from blueprints.auth import auth_bp
from blueprints.dashboard import dashboard_bp
from blueprints.admin import admin_bp

app = Flask(__name__)

# === Security & Middleware ===
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
Talisman(app, content_security_policy={
    "script-src": ["'self'", "https://cdn.plot.ly", "'unsafe-eval'"]
}, force_https=False)

# === Config ===
app.config.update(
    SECRET_KEY=os.getenv("SECRET_KEY", "supersecretkey"),
    SQLALCHEMY_DATABASE_URI=os.getenv("DATABASE_URL", "postgresql://postgres:TATA1tata1@localhost/music_analytics"),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
    SESSION_TYPE="redis",
    SESSION_PERMANENT=True,
    SESSION_KEY_PREFIX="session:",
    SESSION_COOKIE_NAME="music_analytics_session",
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=False,
    REMEMBER_COOKIE_DURATION=timedelta(days=7),
)
app.config['SESSION_REDIS'] = redis.StrictRedis(host='127.0.0.1', port=6379, db=0)

# === Init Extensions ===
db.init_app(app)
bcrypt = Bcrypt(app)
Session(app)
Migrate(app, db)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

# === User Loader ===
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# === Register Blueprints ===
app.register_blueprint(auth_bp, url_prefix="/auth")
app.register_blueprint(dashboard_bp, url_prefix="/dashboard")
app.register_blueprint(admin_bp, url_prefix="/admin")

# === Main Entry ===
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
