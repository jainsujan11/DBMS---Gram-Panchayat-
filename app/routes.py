# app/routes.py
from flask import Blueprint, render_template, session, redirect, url_for, flash
from app.connect import get_db, close_db

app_routes = Blueprint('app_routes', __name__)

@app_routes.route('/')
def index():
    return "Welcome to Gram Panchayat Management System. <a href='/auth/login'>Login</a>"

@app_routes.route('/dashboard')
def dashboard():
    if 'user_type' not in session:
        return redirect(url_for('auth.login'))
    
    user_type = session['user_type']
    if user_type == 'admin':
        return redirect(url_for('admin.admin_dashboard'))
    elif user_type == 'employee':
        return redirect(url_for('employee.employee_dashboard'))
    elif user_type == 'citizen':
        return redirect(url_for('citizen.citizen_dashboard'))
    elif user_type == 'govt':
        return redirect(url_for('govt.govt_dashboard'))
    else:
        flash("Invalid user type.")
        return redirect(url_for('auth.login'))
