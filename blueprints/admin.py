# admin.py
from flask import Blueprint, render_template
from models import User

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

@admin_bp.route("/")
def admin_dashboard():
    users = User.query.all()
    return render_template("admin.html", users=users)
