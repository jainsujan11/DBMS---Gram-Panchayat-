# app/routes.py

from flask import Blueprint, render_template
from .connect import get_db, close_db
from .queries.citizens_queries import get_all_citizens_query

app_routes = Blueprint('app_routes', __name__)

@app_routes.route('/')
def index():
    return render_template('index.html')


@app_routes.route('/citizens')
def citizens():
    conn = get_db()
    cur = conn.cursor()

    # Use the query from citizens_queries.py
    query = get_all_citizens_query()
    cur.execute(query)
    citizens_data = cur.fetchall()  # [(citizen_id, name, gender), ...]

    cur.close()
    close_db(conn)

    # Render citizens.html with fetched data
    return render_template('citizens.html', citizens=citizens_data)
