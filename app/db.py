import os
import psycopg2
from psycopg2 import sql
from configparser import ConfigParser
from werkzeug.security import generate_password_hash

def config(filename='database.ini', section='postgresql'):
    """Read database configuration from a file."""
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

def get_db_connection():
    """Connect to the PostgreSQL database using parameters from the configuration file."""
    params = config()
    conn = psycopg2.connect(**params)
    return conn

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()

    # ---------------------------
    # Create tables
    # ---------------------------

    cur.execute('''
        CREATE TABLE IF NOT EXISTS households (
            household_id SERIAL PRIMARY KEY,
            address TEXT,
            income REAL
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS citizens (
            citizen_id SERIAL PRIMARY KEY,
            name TEXT,
            gender TEXT,
            dob DATE,
            household_id INTEGER,
            educational_qualification TEXT,
            FOREIGN KEY(household_id) REFERENCES households(household_id) ON DELETE CASCADE
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE,
            password TEXT,
            user_type TEXT,
            citizen_id INTEGER,
            FOREIGN KEY(citizen_id) REFERENCES citizens(citizen_id) ON DELETE CASCADE
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS land_records (
            land_id SERIAL PRIMARY KEY,
            citizen_id INTEGER,
            area_acres REAL,
            crop_type TEXT,
            FOREIGN KEY(citizen_id) REFERENCES citizens(citizen_id) ON DELETE CASCADE
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS panchayat_employees (
            employee_id SERIAL PRIMARY KEY,
            citizen_id INTEGER,
            role TEXT,
            FOREIGN KEY(citizen_id) REFERENCES citizens(citizen_id) ON DELETE CASCADE
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS assets (
            asset_id SERIAL PRIMARY KEY,
            type TEXT,
            location TEXT,
            installation_date DATE
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS welfare_schemes (
            scheme_id SERIAL PRIMARY KEY,
            name TEXT,
            description TEXT
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS scheme_enrollments (
            enrollment_id SERIAL PRIMARY KEY,
            citizen_id INTEGER,
            scheme_id INTEGER,
            enrollment_date DATE,
            FOREIGN KEY(citizen_id) REFERENCES citizens(citizen_id) ON DELETE CASCADE,
            FOREIGN KEY(scheme_id) REFERENCES welfare_schemes(scheme_id) ON DELETE CASCADE
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS vaccinations (
            vaccination_id SERIAL PRIMARY KEY,
            citizen_id INTEGER,
            vaccine_type TEXT,
            date_administered DATE,
            FOREIGN KEY(citizen_id) REFERENCES citizens(citizen_id) ON DELETE CASCADE
        )
    ''')

    cur.execute('''
        CREATE TABLE IF NOT EXISTS census_data (
            id SERIAL PRIMARY KEY,
            household_id INTEGER,
            citizen_id INTEGER,
            event_type TEXT,
            event_date DATE,
            FOREIGN KEY(household_id) REFERENCES households(household_id) ON DELETE CASCADE,
            FOREIGN KEY(citizen_id) REFERENCES citizens(citizen_id) ON DELETE CASCADE
        )
    ''')

    # ---------------------------
    # Insert sample data
    # ---------------------------
    # Households
    cur.execute("INSERT INTO households (household_id, address, income) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING", (1, 'Phulera', 90000))
    cur.execute("INSERT INTO households (household_id, address, income) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING", (2, 'Phulera', 120000))
    cur.execute("INSERT INTO households (household_id, address, income) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING", (3, 'Other', 80000))
    
    # Citizens
    citizens_data = [
        ('Alice', 'Female', '2005-06-15', 1, '10th'),
        ('Bob', 'Male', '1995-04-20', 1, 'Graduate'),
        ('Carol', 'Female', '2008-09-10', 2, 'Secondary'),
        ('David', 'Male', '2000-01-02', 2, '10th'),
        ('Eve', 'Female', '1985-03-22', 3, 'Post-Graduate'),
    ]
    user_data = [
        ('Alice', generate_password_hash('Alice123'), 'citizen', 1),
        ('Bob', generate_password_hash('Bob123'), 'citizen', 2),
        ('Carol', generate_password_hash('Carol123'), 'citizen', 3),
        ('David', generate_password_hash('David123'), 'citizen', 4),
        ('Eve', generate_password_hash('Eve123'), 'citizen', 5),
    ]
    for c in citizens_data:
        cur.execute("INSERT INTO citizens (name, gender, dob, household_id, educational_qualification) VALUES (%s, %s, %s, %s, %s) ON CONFLICT DO NOTHING", c)
        
    for c in user_data:
        cur.execute("INSERT INTO users (username, password, user_type, citizen_id) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING", c)
    

    # Land records
    cur.execute("INSERT INTO land_records (citizen_id, area_acres, crop_type) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING", (1, 1.5, 'Rice'))
    cur.execute("INSERT INTO land_records (citizen_id, area_acres, crop_type) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING", (2, 0.8, 'Wheat'))
    cur.execute("INSERT INTO land_records (citizen_id, area_acres, crop_type) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING", (3, 2.0, 'Rice'))
    cur.execute("INSERT INTO land_records (citizen_id, area_acres, crop_type) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING", (4, 1.2, 'Cotton'))

    # Panchayat employees
    cur.execute("INSERT INTO panchayat_employees (citizen_id, role) VALUES (%s, %s) ON CONFLICT DO NOTHING", (2, 'Pradhan'))
    cur.execute("INSERT INTO users (username, password, user_type, citizen_id) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING", ('Bobemp', generate_password_hash('Bob123'), 'employee', 2))
    cur.execute("INSERT INTO panchayat_employees (citizen_id, role) VALUES (%s, %s) ON CONFLICT DO NOTHING", (3, 'Secretary'))
    cur.execute("INSERT INTO users (username, password, user_type, citizen_id) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING", ('Carolemp', generate_password_hash('Carol123'), 'employee', 3))
    cur.execute("INSERT INTO panchayat_employees (citizen_id, role) VALUES (%s, %s) ON CONFLICT DO NOTHING", (4, 'Member'))
    cur.execute("INSERT INTO users (username, password, user_type, citizen_id) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING", ('Davidemp', generate_password_hash('David123'), 'employee', 4))
    
    # Assets
    cur.execute("INSERT INTO assets (type, location, installation_date) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING", ('Street Light', 'Phulera Area 1', '2024-05-10'))
    cur.execute("INSERT INTO assets (type, location, installation_date) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING", ('Street Light', 'Phulera Area 2', '2024-06-15'))
    cur.execute("INSERT INTO assets (type, location, installation_date) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING", ('Water Pump', 'Village C', '2023-07-20'))
    
    # Welfare schemes and enrollments
    cur.execute("INSERT INTO welfare_schemes (name, description) VALUES (%s, %s) ON CONFLICT DO NOTHING", ('Health Scheme', 'Provides free health checkups'))
    cur.execute("INSERT INTO welfare_schemes (name, description) VALUES (%s, %s) ON CONFLICT DO NOTHING", ('Education Scheme', 'Scholarships for students'))
    cur.execute("INSERT INTO scheme_enrollments (citizen_id, scheme_id, enrollment_date) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING", (1, 1, '2023-01-15'))
    cur.execute("INSERT INTO scheme_enrollments (citizen_id, scheme_id, enrollment_date) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING", (3, 2, '2023-02-20'))
    
    # Vaccinations
    cur.execute("INSERT INTO vaccinations (citizen_id, vaccine_type, date_administered) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING", (1, 'Covid-19', '2024-03-10'))
    cur.execute("INSERT INTO vaccinations (citizen_id, vaccine_type, date_administered) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING", (3, 'Polio', '2024-04-12'))
    
    # Census data
    cur.execute("INSERT INTO census_data (household_id, citizen_id, event_type, event_date) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING", (1, 1, 'Birth', '2024-01-05'))
    cur.execute("INSERT INTO census_data (household_id, citizen_id, event_type, event_date) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING", (2, 3, 'Birth', '2024-02-15'))
    cur.execute("INSERT INTO census_data (household_id, citizen_id, event_type, event_date) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING", (1, 2, 'Death', '2022-03-15'))
    
    # Create sample users with hashed passwords
    password_admin = generate_password_hash('admin123')
    password_govt = generate_password_hash('govt123')
    cur.execute("INSERT INTO users (username, password, user_type, citizen_id) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING", ('admin', password_admin, 'admin', None))
    cur.execute("INSERT INTO users (username, password, user_type, citizen_id) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING", ('govt', password_govt, 'govt', None))
    
    # Create a view
    cur.execute('''
        CREATE OR REPLACE VIEW v_citizen AS
        SELECT c.citizen_id, c.name, c.gender, c.dob, c.educational_qualification,
               h.income, h.address,
               l.area_acres, l.crop_type,
               pe.role AS panchayat_role,
               v.vaccine_type, v.date_administered
        FROM citizens c
        JOIN households h ON c.household_id = h.household_id
        LEFT JOIN land_records l ON c.citizen_id = l.citizen_id
        LEFT JOIN panchayat_employees pe ON c.citizen_id = pe.citizen_id
        LEFT JOIN vaccinations v ON c.citizen_id = v.citizen_id
    ''')
    
    conn.commit()
    cur.close()
    conn.close()

if __name__ == '__main__':
    init_db()
