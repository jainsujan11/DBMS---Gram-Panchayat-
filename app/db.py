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
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE,
            password TEXT,
            user_type TEXT,
            citizen_id INTEGER
        )
    ''')
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
            FOREIGN KEY(household_id) REFERENCES households(household_id)
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS land_records (
            land_id SERIAL PRIMARY KEY,
            citizen_id INTEGER,
            area_acres REAL,
            crop_type TEXT,
            FOREIGN KEY(citizen_id) REFERENCES citizens(citizen_id)
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS panchayat_employees (
            employee_id SERIAL PRIMARY KEY,
            citizen_id INTEGER,
            role TEXT,
            FOREIGN KEY(citizen_id) REFERENCES citizens(citizen_id)
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
            FOREIGN KEY(citizen_id) REFERENCES citizens(citizen_id),
            FOREIGN KEY(scheme_id) REFERENCES welfare_schemes(scheme_id)
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS vaccinations (
            vaccination_id SERIAL PRIMARY KEY,
            citizen_id INTEGER,
            vaccine_type TEXT,
            date_administered DATE,
            FOREIGN KEY(citizen_id) REFERENCES citizens(citizen_id)
        )
    ''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS census_data (
            id SERIAL PRIMARY KEY,
            household_id INTEGER,
            citizen_id INTEGER,
            event_type TEXT,
            event_date DATE,
            FOREIGN KEY(household_id) REFERENCES households(household_id),
            FOREIGN KEY(citizen_id) REFERENCES citizens(citizen_id)
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
    for c in citizens_data:
        cur.execute("INSERT INTO citizens (name, gender, dob, household_id, educational_qualification) VALUES (%s, %s, %s, %s, %s) ON CONFLICT DO NOTHING", c)
    
    # Insert additional citizens (~30 rows)
    for i in range(6, 31):
        name = f'Citizen{i}'
        gender = 'Male' if i % 2 == 0 else 'Female'
        dob = '2001-01-01'
        household_id = (i % 3) + 1
        edu = '10th' if i % 2 == 0 else 'Secondary'
        cur.execute("INSERT INTO citizens (name, gender, dob, household_id, educational_qualification) VALUES (%s, %s, %s, %s, %s) ON CONFLICT DO NOTHING", (name, gender, dob, household_id, edu))
    
    # Land records
    cur.execute("INSERT INTO land_records (citizen_id, area_acres, crop_type) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING", (1, 1.5, 'Rice'))
    cur.execute("INSERT INTO land_records (citizen_id, area_acres, crop_type) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING", (2, 0.8, 'Wheat'))
    cur.execute("INSERT INTO land_records (citizen_id, area_acres, crop_type) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING", (3, 2.0, 'Rice'))
    cur.execute("INSERT INTO land_records (citizen_id, area_acres, crop_type) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING", (4, 1.2, 'Cotton'))
    for i in range(6, 16):
        area = 1.0 + (i % 3) * 0.5
        crop = 'Rice' if i % 2 == 0 else 'Wheat'
        cur.execute("INSERT INTO land_records (citizen_id, area_acres, crop_type) VALUES (%s, %s, %s) ON CONFLICT DO NOTHING", (i, area, crop))
    
    # Panchayat employees
    cur.execute("INSERT INTO panchayat_employees (citizen_id, role) VALUES (%s, %s) ON CONFLICT DO NOTHING", (2, 'Pradhan'))
    cur.execute("INSERT INTO panchayat_employees (citizen_id, role) VALUES (%s, %s) ON CONFLICT DO NOTHING", (3, 'Secretary'))
    cur.execute("INSERT INTO panchayat_employees (citizen_id, role) VALUES (%s, %s) ON CONFLICT DO NOTHING", (4, 'Member'))
    
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
    password_emp = generate_password_hash('emp123')
    password_citizen = generate_password_hash('citizen123')
    password_govt = generate_password_hash('govt123')
    cur.execute("INSERT INTO users (username, password, user_type, citizen_id) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING", ('admin', password_admin, 'admin', None))
    cur.execute("INSERT INTO users (username, password, user_type, citizen_id) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING", ('employee', password_emp, 'employee', 2))
    cur.execute("INSERT INTO users (username, password, user_type, citizen_id) VALUES (%s, %s, %s, %s) ON CONFLICT DO NOTHING", ('citizen', password_citizen, 'citizen', 1))
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