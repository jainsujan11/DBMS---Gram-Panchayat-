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

@admin_bp.route('/add_citizen_employee', methods=['GET'])
def add_citizen_employee():
    # Get query parameters
    citizen_id = request.args.get('citizen_id')
    employee_type = request.args.get('employee_type')

    # Validate inputs
    if not citizen_id or not employee_type:
        flash("Both Citizen ID and Employee Type are required", "error")
        return redirect(url_for('admin.admin_dashboard'))

    conn = get_db()
    cur = conn.cursor()

    cur.execute("""SELECT user_type from users where citizen_id=%s""",(citizen_id))
    results = cur.fetchall()

    if(len(results)==0):
        flash(f"No citizen with citizen_id={citizen_id}")
    else:  
        current_type=results[0][0]
        if(current_type==employee_type):
            flash(f"Citizen {citizen_id} is already {current_type}")
        else:
            cur.execute("""UPDATE users set user_type=%s where citizen_id=%s""",(employee_type,citizen_id))
            conn.commit()
            flash(f"Changed user_type of citizen_id {citizen_id} from {current_type} to {employee_type}")
            if(current_type=='citizen'):
                cur.execute("""INSERT INTO panchayat_employees(citizen_id,role) values (%s,%s)""",(citizen_id,employee_type))
            else:
                cur.execute("""UPDATE panchayat_employees set role=%s where citizen_id=%s""",(employee_type,citizen_id))
            conn.commit()
    cur.close()
    close_db()

    return redirect(url_for('admin.admin_dashboard'))

@admin_bp.route('/remove_citizen', methods=['POST'])
def remove_citizen():
    if 'user_type' not in session or session['user_type'] != 'admin':
        flash("Unauthorized access", "error")
        return redirect(url_for('auth.login'))

    # Get the citizen_id from the form
    citizen_id = request.form.get('citizen_id')

    if not citizen_id:
        flash("Citizen ID is required", "error")
        return redirect(url_for('admin.admin_dashboard'))

    # Perform the removal logic (e.g., delete from the database)
    conn = get_db()
    cur = conn.cursor()
    try:
        # Example: Delete the citizen from the citizens table
        cur.execute("DELETE FROM panchayat_employees WHERE citizen_id = %s", (citizen_id,))
        flash(f"Citizen with ID {citizen_id} has been removed successfully", "success")
        cur.execute("UPDATE users set user_type='citizen' where citizen_id=%s",(citizen_id,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        flash(f"An error occurred: {str(e)}", "error")
    finally:
        cur.close()
        close_db()

    # Redirect back to the admin dashboard
    return redirect(url_for('admin.admin_dashboard'))