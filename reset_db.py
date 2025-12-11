"""
Reset the database and reseed with correct admin API key.

Run this ONCE on Render to fix the API key issue.
"""
import os
from app.db.base import Base
from app.db.session import engine
from app.db.session import get_db
from app.seed import seed_database

def reset_database():
    """Drop all tables and recreate with fresh seed data"""
    print("🔄 Resetting database...")
    
    # Drop all tables
    Base.metadata.drop_all(bind=engine)
    print("✓ Dropped all tables")
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    print("✓ Created all tables")
    
    # Seed database
    db = next(get_db())
    try:
        seed_database(db)
        print("\n✅ Database reset complete!")
    finally:
        db.close()

if __name__ == "__main__":
    reset_database()
