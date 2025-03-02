import psycopg2
from configparser import ConfigParser
import os

def load_db_config(filename="database.ini", section="postgresql"):
    parser = ConfigParser()
    base_path = os.path.abspath(os.path.dirname(__file__))
    full_path = os.path.join(base_path, filename)
    parser.read(full_path)
    return {param[0]: param[1] for param in parser.items(section)}

try:
    config = load_db_config()
    conn = psycopg2.connect(**config)
    cursor = conn.cursor()

    drop_query = """
    DO $$ 
    DECLARE 
        r RECORD;
    BEGIN 
        FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') 
        LOOP 
            EXECUTE 'DROP TABLE IF EXISTS ' || r.tablename || ' CASCADE';
        END LOOP; 
    END $$;
    """
    
    cursor.execute(drop_query)
    conn.commit()
    
    print("All tables dropped successfully!")
    cursor.close()
    conn.close()
except Exception as e:
    print("Error:", e)
