# app/employee.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.connect import get_db, close_db  # Fix import

employee_bp = Blueprint('employee', __name__)

@employee_bp.route('/')
def employee_dashboard():
    if 'user_type' not in session or session['user_type'] != 'employee':
        flash("Unauthorized access")
        return redirect(url_for('auth.login'))
    return render_template('employee_dashboard.html')

@employee_bp.route('/query', methods=['GET', 'POST'])
def employee_query_select():
    if 'user_type' not in session or session['user_type'] != 'employee':
        flash("Unauthorized access")
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
        query_category = request.form.get('query_category')
        return redirect(url_for('employee.employee_query_form', query_type=query_category))
    return render_template('employee_query_select.html')

@employee_bp.route('/query/<query_type>', methods=['GET', 'POST'])
def employee_query_form(query_type):
    if 'user_type' not in session or session['user_type'] != 'employee':
        flash("Unauthorized access")
        return redirect(url_for('auth.login'))

    results = None
    if request.method == 'POST':
        conn = get_db()
        cur = conn.cursor()
        query = "SELECT * FROM citizens WHERE name ILIKE %s"
        params = (f"%{request.form.get('name')}%",)
        cur.execute(query, params)
        results = cur.fetchall()
        cur.close()
        close_db(conn)

    return render_template('employee_query_form.html', query_type=query_type, results=results)
