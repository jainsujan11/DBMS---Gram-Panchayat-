# app/govt.py
from flask import Blueprint, render_template, session, flash, redirect, url_for,request
from connect import get_db, close_db  # Fix import

govt_bp = Blueprint('govt', __name__)

@govt_bp.route('/', methods=['GET', 'POST'])
def govt_dashboard():
    if 'user_type' not in session or session['user_type'] != 'govt':
        flash("Unauthorized access")
        return redirect(url_for('auth.login'))
    return render_template('govt.html')

#respond to GET requests , accept POST requests
@govt_bp.route('/add_scheme',methods=['GET','POST'])
def govt_add_scheme():
    if request.method == 'GET':
        #first render html page to get response
        return render_template('govt_add_scheme.html')
    else:   
        #here we get response
        scheme_number = request.form.get('scheme_number')
        scheme_name = request.form.get('scheme_name')
        scheme_description = request.form.get('scheme_description')

        conn = get_db()
        cur = conn.cursor()
        
        try:
            cur.execute("insert into welfare_schemes values (%s,%s,%s)",(scheme_number,scheme_name,scheme_description))
            conn.commit() #important
            conn.close()
            flash("welfare scheme added successfully.")
        except Exception as e:
            flash("Welface scheme addition failed")
            flash(f"Error: {e}")
            conn.close()

        return redirect(url_for('govt.govt_add_scheme'))

@govt_bp.route('/print_statistics',methods=['POST'])
def govt_print_statistics():
    which_query=request.form.get('which_query')
    query=None
    if(which_query=='Birth_Rate'):
        # query="select * from birth_rate"  #select gender,count(*) from citizens where EXTRACT(YEAR FROM dob) = 2001 group by gender
        query="select EXTRACT(YEAR FROM dob) as year,gender,count(*) as count from citizens group by EXTRACT(YEAR FROM dob),gender"
    elif(which_query=='Literacy_Rate'):
        # query="select * from literacy_rate" #select * from citizens where educational_qualification != 'Secondary';
        query="select * from citizens where educational_qualification != 'Secondary';"
    elif(which_query == 'Assets'):
        query="select * from assets"
    elif(which_query == 'Poverty Line'):
        query="select 'BELOW POVERTY LINE' as Stats,count(*) as count from households where income < (select avg(income) from households)" 
    elif(which_query =='Scheme Enrollments'):
        query="select scheme_id,count(*) as count from scheme_enrollments group by scheme_id"

    conn = get_db()
    cur = conn.cursor()
    cur.execute(query)
    results = cur.fetchall()

    column_names = [desc[0] for desc in cur.description]

    print(results,column_names)

    conn.close()
    if(which_query=='Birth_Rate'):
        return render_template('display_graph.html',data=results)
    return render_template('employee_query_result.html',query_type=which_query,results=results,column_names=column_names)