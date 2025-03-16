from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

# Database URL - use environment variable or default to PostgreSQL
# Format: postgresql://username:password@localhost:5432/database_name
# If no password is set, use a simpler URL format
user = os.getenv("POSTGRES_USER", "harismac")
password = os.getenv("POSTGRES_PASSWORD", "")
host = os.getenv("POSTGRES_HOST", "localhost")
port = os.getenv("POSTGRES_PORT", "5432")
db = os.getenv("POSTGRES_DB", "allergen_app")

if password:
    DATABASE_URL = f"postgresql://{user}:{password}@{host}:{port}/{db}"
else:
    DATABASE_URL = f"postgresql://{user}@{host}:{port}/{db}"

# Override with explicit DATABASE_URL if provided
DATABASE_URL = os.getenv("DATABASE_URL", DATABASE_URL)

# Create SQLAlchemy engine with PostgreSQL
engine = create_engine(DATABASE_URL)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class
Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 