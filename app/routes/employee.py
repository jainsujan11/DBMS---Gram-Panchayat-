from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from connect import get_db, close_db
import psycopg2
import psycopg2.extras

employee_bp = Blueprint('employee', __name__)

@employee_bp.route('/')
def employee_dashboard():
    if 'user_type' not in session or (session['user_type'] != 'employee' and session['user_type'] != 'citizen'):
        flash("Unauthorized access")
        return redirect(url_for('auth.login'))
    return render_template('employee_dashboard.html')

# -----------------------------
# Dynamic Query Module
# -----------------------------
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
    if 'user_type' not in session or (session['user_type'] != 'employee' and session['user_type'] != 'citizen'):
        flash("Unauthorized access")
        return redirect(url_for('auth.login'))
    results = None
    if request.method == 'POST':
        conn = get_db()
        cur = conn.cursor()
        if query_type == 'citizen':
            name = request.form.get('name')
            gender = request.form.get('gender')
            edu = request.form.get('educational_qualification')
            min_land = request.form.get('min_land')
            max_income = request.form.get('max_income')
            dob = request.form.get('dob')
            is_pradhan = request.form.get('is_pradhan')
            is_employee = request.form.get('is_employee')
            is_household = request.form.get('is_household')
            vacc_year = request.form.get('vaccination_year')
            query_select="select citizen_id,name,gender,dob,household_id,educational_qualification"
            query_from="from citizens "
            query_where="where 1=1"
            query_group_by="group by citizen_id,name,gender,dob,household_id,educational_qualification"
            query_having="having 1=1"
            group_by=0


            params_where = []
            params_having = []
            params = []
            if name:
                query_where+=" AND name ILIKE %s"
                params_where.append('%' + name + '%')
            if gender and gender != "Any":
                query_where += " AND gender = %s"
                params_where.append(gender)
            if edu:
                # query += " AND educational_qualification ILIKE %s"
                query_where += " AND educational_qualification ILIKE %s"
                params_where.append('%' + edu + '%')
            if min_land:
                query_select+=",sum(area_acres)"
                query_from+=" join land_records using (citizen_id)"
                query_having+=" and sum(area_acres) >= %s"
                params_having.append(min_land)
                group_by=1
            if max_income:
                query_select+=",income"
                query_from+="  join households using (household_id)"
                query_having+=" and income <= %s"
                query_group_by += ",income"
                params_having.append(max_income)
                group_by=1
            if dob:
                query_where += " AND dob > %s"
                params_where.append(dob)
            if is_pradhan == 'on':
                query_from  +="  join panchayat_employees using (citizen_id)"
                query_where += " AND role = 'Pradhan'"
            if is_employee == 'on':
                if is_pradhan != 'on':
                    query_select += ",role"
                    query_from += "  join panchayat_employees using (citizen_id)"
                    query_group_by += ",role"
            if vacc_year:
                # query += " AND EXTRACT(YEAR FROM date_administered) = %s"
                query_select+=",date_administered"
                query_from += " join vaccinations using (citizen_id)"
                query_where += " AND EXTRACT(YEAR FROM installation_date) = %s"
                query_group_by+=" ,date_administered"
                params_where.append(vacc_year)
            if is_household == 'on':
                query_from += " join citizens as C2(_citizen_id,_name,_gender,_dob,household_id,_educational_qualification) using (household_id)"
                query_where += " AND household_id = C2.household_id"
                query_select += ",C2._citizen_id as family_member_id, C2._name as family_member_name"

            query=query_select+"\n"+query_from+"\n"+query_where
            if(group_by):
                query+="\n"+query_group_by+"\n"+query_having
            params = params_where+params_having
            cur.execute(query, tuple(params))
            results = cur.fetchall()
        
        elif query_type == 'asset':
            locality = request.form.get('locality')
            year = request.form.get('year')
            asset_type = request.form.get('asset_type')
            query = "SELECT * FROM assets WHERE 1=1"
            params = []
            if locality:
                query += " AND location ILIKE %s"
                params.append('%' + locality + '%')
            if year:
                query += " AND EXTRACT(YEAR FROM installation_date) = %s"
                params.append(year)
            if asset_type:
                query += " AND type = %s"
                params.append(asset_type)
            cur.execute(query, tuple(params))
            results = cur.fetchall()
        
        elif query_type == 'land':
            crop = request.form.get('crop')
            query = "SELECT * FROM land_records WHERE 1=1"
            params = []
            if crop:
                query += " AND crop_type ILIKE %s"
                params.append('%' + crop + '%')
            cur.execute(query, tuple(params))
            results = cur.fetchall()

        # print query in console in good format
        print(cur.mogrify(query, tuple(params)))

        conn.close()
        return render_template('employee_query_result.html', query_type=query_type, results=results)
    return render_template('employee_query_form.html', query_type=query_type, results=results)

# -----------------------------
# Add/Modify Module
# -----------------------------
@employee_bp.route('/add', methods=['GET'])
def employee_add_select():
    if 'user_type' not in session or session['user_type'] != 'employee':
        flash("Unauthorized access")
        return redirect(url_for('auth.login'))
    return render_template('employee_add_select.html')

@employee_bp.route('/add/citizen', methods=['GET', 'POST'])
def employee_add_citizen():
    if 'user_type' not in session or session['user_type'] != 'employee':
        flash("Unauthorized access")
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        hashed_password = generate_password_hash(password)
        name = request.form.get('name')
        gender = request.form.get('gender')
        dob = request.form.get('dob')
        educational_qualification = request.form.get('educational_qualification')
        household_id = request.form.get('household_id')
        conn = get_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO citizens (name, gender, dob, household_id, educational_qualification) VALUES (%s, %s, %s, %s, %s)\
                    RETURNING citizen_id",(name, gender, dob, household_id, educational_qualification))
        citizen_id = cur.fetchone()[0]  # Get the newly inserted citizen_id

        # Insert into users table using form values
        cur.execute(
            "INSERT INTO users (citizen_id, username, password, user_type) VALUES (%s, %s,%s, %s)",
            (citizen_id, username, hashed_password, "citizen")
        )
        conn.commit()
        conn.close()
        flash("Citizen record added successfully.")
        return redirect(url_for('employee.employee_add_select'))
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM households")  # Execute the query
    households = cur.fetchall()  # Fetch all results
    conn.close()
    return render_template('employee_add_citizen.html', households=households)

@employee_bp.route('/add/land', methods=['GET', 'POST'])
def employee_add_land():
    if 'user_type' not in session or session['user_type'] != 'employee':
        flash("Unauthorized access")
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
        citizen_id = request.form.get('citizen_id')
        area_acres = request.form.get('area_acres')
        crop_type = request.form.get('crop_type')
        conn = get_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO land_records (citizen_id, area_acres, crop_type) VALUES (%s, %s, %s)",
                    (citizen_id, area_acres, crop_type))
        conn.commit()
        conn.close()
        flash("Land record added successfully.")
        return redirect(url_for('employee.employee_add_select'))
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT citizen_id, name FROM citizens")
    citizens = cur.fetchall()
    conn.close()
    return render_template('employee_add_land.html', citizens=citizens)

@employee_bp.route('/add/asset', methods=['GET', 'POST'])
def employee_add_asset():
    if 'user_type' not in session or session['user_type'] != 'employee':
        flash("Unauthorized access")
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
        asset_type = request.form.get('asset_type')
        location = request.form.get('location')
        installation_date = request.form.get('installation_date')
        conn = get_db()
        cur = conn.cursor()
        cur.execute("INSERT INTO assets (type, location, installation_date) VALUES (%s,%s,%s)",
                    (asset_type, location, installation_date))
        conn.commit()
        conn.close()
        flash("Asset record added successfully.")
        return redirect(url_for('employee.employee_add_select'))
    return render_template('employee_add_asset.html')


@employee_bp.route('/modify_citizen')
def employee_modify_citizen():
    # Get citizen_id from the query parameters
    citizen_id = request.args.get('citizen_id')

    if not citizen_id:
        flash("Citizen ID is required", "error")
        return redirect(url_for('employee.employee_dashboard'))

    # Fetch citizen details from the database
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM citizens WHERE citizen_id = %s", (citizen_id,))
    citizen = cur.fetchone()
    cur.close()
    close_db()

    if not citizen:
        flash("Citizen not found", "error")
        return redirect(url_for('employee.employee_dashboard'))

    # Pass citizen details to the template
    return render_template('modify_citizen.html', citizen=citizen)


@employee_bp.route('/update_citizen/<int:citizen_id>', methods=['POST'])
def update_citizen(citizen_id):
    # Get form data
    name = request.form.get('name')
    gender = request.form.get('gender')
    dob = request.form.get('dob')
    household_id = request.form.get('household_id')
    educational_qualification = request.form.get('educational_qualification')

    # Validate form data
    if not all([name, gender, dob, household_id, educational_qualification]):
        flash("All fields are required", "error")
        return redirect(url_for('employee.employee_modify_citizen', citizen_id=citizen_id))

    # Update citizen details in the database
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute("""
            UPDATE citizens
            SET name = %s,
                gender = %s,
                dob = %s,
                household_id = %s,
                educational_qualification = %s
            WHERE citizen_id = %s
        """, (name, gender, dob, household_id, educational_qualification, citizen_id))
        conn.commit()
        flash("Citizen details updated successfully", "success")
    except Exception as e:
        conn.rollback()
        flash(f"An error occurred: {str(e)}", "error")
    finally:
        cur.close()
        close_db()

    # Redirect back to the modify page
    return redirect(url_for('employee.employee_modify_citizen', citizen_id=citizen_id))


@employee_bp.route('/add_citizen_to_scheme', methods=['GET'])
def employee_add_citizen_to_scheme():
    if 'user_type' not in session or session['user_type'] != 'employee':
        flash("Unauthorized access")
        return redirect(url_for('auth.login'))

    # Fetch all citizen IDs from the citizens table
    conn = get_db()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT citizen_id FROM citizens")
    citizens = cur.fetchall()

    # Fetch all scheme IDs from the welfare_schemes table
    cur.execute("SELECT scheme_id FROM welfare_schemes")
    schemes = cur.fetchall()

    cur.close()
    close_db()

    # Render the HTML template with the fetched data
    return render_template('add_citizen_to_scheme.html', citizens=citizens, schemes=schemes)

@employee_bp.route('/submit_citizen_to_scheme', methods=['POST'])
def submit_citizen_to_scheme():
    if 'user_type' not in session or session['user_type'] != 'employee':
        flash("Unauthorized access")
        return redirect(url_for('auth.login'))

    # Get form data
    citizen_id = request.form.get('citizen_id')
    scheme_id = request.form.get('scheme_id')
    date_of_enrollment = request.form.get('date_of_enrollment')

    # Validate form data
    if not all([citizen_id, scheme_id, date_of_enrollment]):
        flash("All fields are required", "error")
        return redirect(url_for('employee.employee_add_citizen_to_scheme'))

    # Insert data into the database
    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO scheme_enrollments (citizen_id, scheme_id, enrollment_date)
            VALUES (%s, %s, %s)
        """, (citizen_id, scheme_id, date_of_enrollment))
        conn.commit()
        flash("Citizen added to scheme successfully", "success")
    except Exception as e:
        conn.rollback()
        flash(f"An error occurred: {str(e)}", "error")
    finally:
        cur.close()
        close_db()

    # Redirect back to the add citizen to scheme page
    return redirect(url_for('employee.employee_add_citizen_to_scheme'))