# app/__init__.py
from flask import Flask
from app.connect import close_db
from app.auth import auth_bp
from app.admin import admin_bp
from app.citizen import citizen_bp
from app.employee import employee_bp
from app.govt import govt_bp
from app.routes import app_routes

def create_app():
    app = Flask(__name__)
    app.secret_key = "supersecretkey"  # Required for session management

    # Register blueprints
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(citizen_bp, url_prefix='/citizen')
    app.register_blueprint(employee_bp, url_prefix='/employee')
    app.register_blueprint(govt_bp, url_prefix='/govt')
    app.register_blueprint(app_routes)  # Main routes

    return app
