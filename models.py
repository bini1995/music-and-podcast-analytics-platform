from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from itsdangerous import URLSafeTimedSerializer
import pyotp
import redis
from datetime import datetime, timedelta
from flask_login import UserMixin
import secrets
#from app import db

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:TATA1tata1@localhost/music_analytics'
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['SESSION_PERMANENT'] = False  # Allows session timeout
app.config['SESSION_LIFETIME'] = timedelta(minutes=30)  # Auto logout after 30 min inactivity

# Initialize services
db = SQLAlchemy()
db.init_app(app)
bcrypt = Bcrypt(app)
serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

# Enforce Password Complexity
PASSWORD_MIN_LENGTH = 8
PASSWORD_COMPLEXITY_RULES = {
    "uppercase": 1, "lowercase": 1, "digit": 1, "special": 1
}

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='user')
    last_active = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    password_history = db.Column(db.JSON, default=list, nullable=False)
    password_last_changed = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # ✅ Password Reset Fields
    password_reset_token = db.Column(db.String(255), nullable=True, unique=True)
    reset_token_expiry = db.Column(db.DateTime, nullable=True)

    # ✅ 2FA Fields
    two_factor_enabled = db.Column(db.Boolean, default=False)
    two_factor_secret = db.Column(db.String(32), nullable=True)

    def generate_reset_token(self, expiration_minutes=15):
        """Generate password reset token"""
        self.password_reset_token = secrets.token_urlsafe(32)
        self.reset_token_expiry = datetime.utcnow() + timedelta(minutes=expiration_minutes)
        db.session.commit()
        return self.password_reset_token

    def verify_reset_token(self, token):
        """Verify password reset token"""
        return self.password_reset_token == token and datetime.utcnow() < self.reset_token_expiry

    def update_last_active(self):
        """ Update last_active timestamp """
        self.last_active = datetime.utcnow()
        db.session.commit()

    def set_password(self, password):
        if not self.validate_password_complexity(password):
            raise ValueError("Password does not meet complexity requirements.")
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        if self.password_history:
            if hashed_password in self.password_history:
                raise ValueError("Cannot reuse old passwords.")
            if len(self.password_history) >= 5:
                self.password_history.pop(0)
        self.password_history = (self.password_history or []) + [hashed_password]
        self.password_hash = hashed_password
        self.password_last_changed = datetime.utcnow()

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def generate_2fa_secret(self):
        self.two_factor_secret = pyotp.random_base32()
        return self.two_factor_secret

    def get_otp_uri(self):
        return pyotp.totp.TOTP(self.two_factor_secret).provisioning_uri(
            self.email, issuer_name="Music Analytics Platform"
        )

    def verify_otp(self, otp):
        totp = pyotp.TOTP(self.two_factor_secret)
        return totp.verify(otp)

    @staticmethod
    def validate_password_complexity(password):
        if len(password) < PASSWORD_MIN_LENGTH:
            return False
        rules = {"uppercase": 0, "lowercase": 0, "digit": 0, "special": 0}
        for char in password:
            if char.isupper():
                rules["uppercase"] += 1
            elif char.islower():
                rules["lowercase"] += 1
            elif char.isdigit():
                rules["digit"] += 1
            elif not char.isalnum():
                rules["special"] += 1
        return all(rules[key] >= PASSWORD_COMPLEXITY_RULES[key] for key in PASSWORD_COMPLEXITY_RULES)

    # ✅ Flask-Login integration
    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        """ Check if user has been active in the last 30 minutes """
        return self.last_active and (datetime.utcnow() - self.last_active < timedelta(minutes=30))

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)
    
class StreamingMetrics(db.Model):
    """Stores streaming analytics from Spotify."""
    id = db.Column(db.Integer, primary_key=True)
    song_name = db.Column(db.String(255), nullable=False)
    artist_name = db.Column(db.String(255), nullable=False)
    album_name = db.Column(db.String(255), nullable=True)
    plays = db.Column(db.Integer, default=0)
    saves = db.Column(db.Integer, default=0)  # Newly added
    shares = db.Column(db.Integer, default=0)  # Newly added
    likes = db.Column(db.Integer, default=0)  # Newly added

    def __repr__(self):
        return f"<StreamingMetrics {self.song_name} - {self.artist_name}>"


# Ensure app runs only when script is executed
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
