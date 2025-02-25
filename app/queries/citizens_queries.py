# app/queries/citizens_queries.py

def get_all_citizens_query():
    return "SELECT citizen_id, name, gender FROM citizens;"
