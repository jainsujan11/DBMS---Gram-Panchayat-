# app/admin.py
from flask import Blueprint, render_template, request, flash, session, redirect, url_for
from app.connect import get_db, close_db  # Fix import

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/', methods=['GET', 'POST'])
def admin_dashboard():
    if 'user_type' not in session or session['user_type'] != 'admin':
        flash("Unauthorized access")
        return redirect(url_for('auth.login'))
    
    result = None
    query_executed = ""

    if request.method == 'POST':
        query = request.form['query']
        conn = get_db()
        cur = conn.cursor()
        try:
            cur.execute(query)
            result = cur.fetchall()  # Fetch result of query
            conn.commit()
            query_executed = query
        except Exception as e:
            flash("Error executing query: " + str(e))
        finally:
            cur.close()
            close_db(conn)

    return render_template('admin.html', result=result, query_executed=query_executed)
