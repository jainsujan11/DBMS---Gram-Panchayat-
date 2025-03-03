# app/routes.py
from flask import Blueprint, render_template, session, redirect, url_for, flash, Flask
from connect import get_db, close_db
from routes.auth import auth_bp
from routes.admin import admin_bp
from routes.employee import employee_bp
from routes.citizen import citizen_bp
from routes.govt import govt_bp

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change for production

# Register blueprints
app.register_blueprint(auth_bp)  # no prefix (login, signup, logout)
app.register_blueprint(admin_bp, url_prefix='/admin')
app.register_blueprint(employee_bp, url_prefix='/employee')
app.register_blueprint(citizen_bp, url_prefix='/citizen')
app.register_blueprint(govt_bp, url_prefix='/govt')

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/dashboard')
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

if __name__ == '__main__':
    app.run(debug=True)
