import sqlite3
import os
import sys

# Ensure root directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import Config

def get_db_connection(db_path=None):
    """Establishes and returns a database connection with Row factory."""
    if db_path is None:
        db_path = Config.DATABASE_PATH
    
    # Ensure parent directory exists
    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db(db_path=None):
    """Initializes the database using schema.sql."""
    if db_path is None:
        db_path = Config.DATABASE_PATH
        
    schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
    print(f"[*] Initializing database at: {db_path}")
    
    conn = get_db_connection(db_path)
    with open(schema_path, 'r', encoding='utf-8') as f:
        conn.executescript(f.read())
    conn.commit()
    conn.close()
    print("[+] Database initialized successfully.")

if __name__ == '__main__':
    target = sys.argv[1] if len(sys.argv) > 1 else None
    init_db(target)
