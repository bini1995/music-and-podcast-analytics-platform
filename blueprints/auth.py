# auth.py
from flask import Blueprint, request, jsonify, redirect, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from models import db, User
from functools import wraps
import re
from flask_bcrypt import Bcrypt

auth_bp = Blueprint("auth", __name__)
bcrypt = Bcrypt()

# Helpers
def is_valid_username(username):
    return re.match(r'^[a-zA-Z0-9]{4,20}$', username)

def is_valid_password(password):
    return re.match(r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d).{8,}$', password)

def role_required(role):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated or current_user.role != role:
                return jsonify({"error": "Insufficient privileges"}), 403
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Routes
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.json
    user = User.query.filter_by(username=data.get("username")).first()
    if user and user.check_password(data.get("password")):
        login_user(user, remember=True)
        return jsonify({"message": "Login successful"})
    return jsonify({"error": "Invalid credentials"}), 401

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.json
    if not is_valid_username(data.get("username")) or not is_valid_password(data.get("password")):
        return jsonify({"error": "Invalid input"}), 400
    hashed = bcrypt.generate_password_hash(data["password"]).decode("utf-8")
    new_user = User(username=data["username"], email=data["email"], password_hash=hashed)
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"message": "Registered successfully"}), 201



@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out.")
    return redirect("/")
