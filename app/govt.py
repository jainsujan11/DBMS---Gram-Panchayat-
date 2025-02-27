# app/govt.py
from flask import Blueprint, render_template, session, flash, redirect, url_for
from app.connect import get_db, close_db  # Fix import

govt_bp = Blueprint('govt', __name__)

@govt_bp.route('/', methods=['GET', 'POST'])
def govt_dashboard():
    if 'user_type' not in session or session['user_type'] != 'govt':
        flash("Unauthorized access")
        return redirect(url_for('auth.login'))

    conn = get_db()
    cur = conn.cursor()

    cur.execute("SELECT SUM(area_acres) FROM land_records WHERE crop_type = 'Rice'")
    total_rice = cur.fetchone()[0]  # Fetch as tuple

    cur.execute("SELECT COUNT(*) FROM citizens")
    total_citizens = cur.fetchone()[0]  # Fetch as tuple

    cur.close()
    close_db(conn)

    stats = {'total_rice': total_rice, 'total_citizens': total_citizens}
    return render_template('govt.html', stats=stats)
