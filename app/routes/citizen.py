# app/citizen.py
from flask import Blueprint, render_template, session, flash, redirect, url_for
import psycopg2
import psycopg2.extras
from connect import get_db, close_db  # Fix import

citizen_bp = Blueprint('citizen', __name__)

@citizen_bp.route('/')
def citizen_dashboard():
    if 'user_type' not in session or session['user_type'] != 'citizen':
        flash("Unauthorized access")
        return redirect(url_for('auth.login'))

    citizen_id = session.get('citizen_id')
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM citizens WHERE citizen_id = %s", (citizen_id,))
    citizen = cur.fetchone()
    # convert it to a dictionary
    cur.execute("SELECT * FROM land_records WHERE citizen_id = %s", (citizen_id,))
    lands = cur.fetchall()

    cur.execute("SELECT * FROM vaccinations WHERE citizen_id = %s", (citizen_id,))
    vaccinations = cur.fetchall()

    cur.execute("SELECT * FROM scheme_enrollments WHERE citizen_id = %s", (citizen_id,))
    enrollments = cur.fetchall()

    cur.close()
    close_db()

    return render_template('citizen.html', citizen=citizen, lands=lands, vaccinations=vaccinations, enrollments=enrollments)
