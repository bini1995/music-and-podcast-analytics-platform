from flask import Blueprint

# Import all blueprints
from .auth import auth_bp
from .dashboard import dashboard_bp
from .admin import admin_bp

blueprints = [auth_bp, dashboard_bp, admin_bp]
