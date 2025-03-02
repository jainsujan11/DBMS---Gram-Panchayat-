# app/admin.py
from flask import Blueprint, render_template, request, flash, session, redirect, url_for
from connect import get_db, close_db  # Fix import
import psycopg2
import psycopg2.extras


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
        cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        try:
            cur.execute(query)
            result = cur.fetchall()  # Fetch result of query
            conn.commit()
            query_executed = query
        except Exception as e:
            flash("Error executing query: " + str(e))
        finally:
            cur.close()
            close_db()

    return render_template('admin.html', result=result, query_executed=query_executed)
