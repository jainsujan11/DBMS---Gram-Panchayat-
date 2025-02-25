# app/connect.py
import psycopg2  # or any other DB adapter
from configparser import ConfigParser
from flask import g
import os 
def config(filename='database.ini', section='postgresql'):
    parser = ConfigParser()
    base_path = os.path.abspath(os.path.dirname(__file__))
    full_path = os.path.join(base_path, filename)
    parser.read(full_path)
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception(f'Section {section} not found in {filename}')
    return db

def get_db():
    if 'db' not in g:
        params = config()
        g.db = psycopg2.connect(**params)
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()
