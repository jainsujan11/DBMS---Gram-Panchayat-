# app/citizen.py
from flask import Blueprint, render_template, session, flash, redirect, url_for, request
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



@citizen_bp.route('/view_household_members')
def view_household_members():
    household_id = request.args.get('household_id')
    citizen_id = request.args.get('citizen_id')
    query_select="select citizen_id,name,gender,dob,household_id,educational_qualification"
    query_from="from citizens "
    query_where="where citizen_id = %s"
    query_group_by="group by citizen_id,name,gender,dob,household_id,educational_qualification"
    query_having="having 1=1"
    group_by=0
    query_from += " join citizens as C2(_citizen_id,_name,_gender,_dob,household_id,_educational_qualification) using (household_id)"
    query_where += " AND %s = C2.household_id"
    query_select += ",C2._citizen_id as family_member_id, C2._name as family_member_name"
    query=query_select+"\n"+query_from+"\n"+query_where
    if(group_by):
        query+="\n"+query_group_by+"\n"+query_having
    params = []
    params.append(citizen_id)
    params.append(household_id)
    conn = get_db()
    cur = conn.cursor()
    cur.execute(query, params)
    results = cur.fetchall()
    conn.close()
    return render_template('employee_query_result.html', query_type="", results=results)
    pass