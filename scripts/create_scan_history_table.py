#!/usr/bin/env python3
import os
import sys
import sqlite3
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Import the database connection
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.core.database import engine, Base, SessionLocal
from app.models.scan_history import ScanHistory
from app.models.user import User

def create_tables():
    """Create the necessary tables in the database."""
    try:
        # Create the users table first (if it doesn't exist)
        Base.metadata.create_all(bind=engine, tables=[User.__table__])
        print("Users table created or already exists.")
        
        # Create the scan_history table
        Base.metadata.create_all(bind=engine, tables=[ScanHistory.__table__])
        print("Scan history table created successfully.")
    except Exception as e:
        print(f"Error creating tables: {e}")
        sys.exit(1)

if __name__ == "__main__":
    create_tables() 