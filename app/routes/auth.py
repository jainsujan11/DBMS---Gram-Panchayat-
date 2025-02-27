# app/auth.py
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from connect import get_db, close_db  # Use correct import

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        conn = get_db()
        cur = conn.cursor()

        # Fetch user from DB
        cur.execute("SELECT id, password, user_type, citizen_id FROM users WHERE username = %s", (username,))
        user = cur.fetchone()  # Returns tuple: (id, password_hash, user_type, citizen_id)
        print(user)
        cur.close()
        close_db(conn)

        if user and check_password_hash(user[1], password):  # Check hashed password
            session['user_id'] = user[0]
            session['user_type'] = user[2]
            session['citizen_id'] = user[3]
            flash("Logged in successfully!")
            return redirect(url_for('dashboard'))  # Redirect to dashboard
        else:
            flash("Invalid credentials")
            return redirect(url_for('auth.login'))  # Redirect back to login

    return render_template('login.html')


@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user_type = request.form['user_type']

        conn = get_db()
        cur = conn.cursor()
        hashed_password = generate_password_hash(password)
        citizen_id = None  # Default

        if user_type == 'citizen':
            name = request.form['name']
            gender = request.form['gender']
            dob = request.form['dob']
            educational_qualification = request.form['educational_qualification']
            household_choice = request.form.get('household_choice')
            # Handle new or existing household
            if household_choice == 'new':
                address = request.form['address']
                income = request.form['income']
                cur.execute("INSERT INTO households (address, income) VALUES (%s, %s) RETURNING household_id;", (address, income))
                household_id = cur.fetchone()[0]  # Get new household ID
            else:
                household_id = request.form['existing_household']

            # Insert Citizen
            cur.execute("""
                INSERT INTO citizens (name, gender, dob, household_id, educational_qualification) 
                VALUES (%s, %s, %s, %s, %s) RETURNING citizen_id;
            """, (name, gender, dob, household_id, educational_qualification))
            citizen_id = cur.fetchone()[0]  # Get new citizen ID

        try:
            # Insert User
            cur.execute("INSERT INTO users (username, password, user_type, citizen_id) VALUES (%s, %s, %s, %s)",
                        (username, hashed_password, user_type, citizen_id))
            conn.commit()
            flash("Signup successful, please login.")
            return redirect(url_for('auth.login'))

        except Exception as e:
            conn.rollback()  # Undo changes if error occurs
            flash("Error during signup: " + str(e))
            return redirect(url_for('auth.signup'))

        finally:
            cur.close()
            close_db(conn)

    # Fetch existing households for dropdown
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT household_id, address FROM households")
    households = cur.fetchall()
    cur.close()
    close_db(conn)

    return render_template('signup.html', households=households)


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully.")
    return redirect(url_for('auth.login'))
