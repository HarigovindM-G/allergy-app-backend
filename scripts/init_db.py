import psycopg2
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add the parent directory to the path so we can import from app
sys.path.append(str(Path(__file__).parent.parent))

# Load environment variables
load_dotenv(Path(__file__).parent.parent / '.env')

from app.core.database import Base, engine

def init_db():
    """Initialize the database by creating all tables."""
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully!")
    except Exception as e:
        print(f"Error creating database tables: {e}")
        sys.exit(1)

def create_database():
    """Create the database if it doesn't exist."""
    # Default connection parameters
    dbname = "postgres"  # Connect to default postgres database first
    user = os.getenv("POSTGRES_USER", "harismac")
    password = os.getenv("POSTGRES_PASSWORD", "")
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    
    # Target database name
    target_db = os.getenv("POSTGRES_DB", "allergen_app")
    
    try:
        # Connect to default postgres database
        conn_params = {
            "dbname": dbname,
            "user": user,
            "host": host,
            "port": port
        }
        
        # Only add password if it's set
        if password:
            conn_params["password"] = password
            
        conn = psycopg2.connect(**conn_params)
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Check if database exists
        cursor.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{target_db}'")
        exists = cursor.fetchone()
        
        if not exists:
            print(f"Creating database '{target_db}'...")
            cursor.execute(f"CREATE DATABASE {target_db}")
            print(f"Database '{target_db}' created successfully!")
        else:
            print(f"Database '{target_db}' already exists.")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"Error connecting to PostgreSQL: {e}")
        sys.exit(1)

if __name__ == "__main__":
    create_database()
    init_db() 