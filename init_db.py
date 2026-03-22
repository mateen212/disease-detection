#!/usr/bin/env python3
"""
Database initialization script for Disease Diagnosis System
Run this script to set up the database tables and sample data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.db.database import create_tables, engine, SessionLocal
from backend.models.database_models import Base, Admin
from sqlalchemy import text
from passlib.hash import bcrypt
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database():
    """Initialize database with tables and sample data"""
    try:
        logger.info("🔧 Initializing database...")
        
        # Create all tables
        logger.info("📋 Creating database tables...")
        create_tables()
        logger.info("✅ Database tables created successfully")
        
        # Test connection
        logger.info("🔗 Testing database connection...")
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            if result.fetchone():
                logger.info("✅ Database connection successful")
            else:
                raise Exception("Database connection test failed")
        
        # Seed initial admin user (if configured)
        admin_username = os.getenv("ADMIN_USERNAME", "admin")
        admin_password = os.getenv("ADMIN_PASSWORD", "adminpass")

        logger.info("🔐 Ensuring admin user exists...")
        db = SessionLocal()
        try:
            existing = db.query(Admin).filter(Admin.username == admin_username).first()
            if existing:
                logger.info(f"ℹ️ Admin user '{admin_username}' already exists (id={existing.id})")
            else:
                hashed = bcrypt.hash(admin_password)
                admin = Admin(username=admin_username, hashed_password=hashed, is_active=1)
                db.add(admin)
                db.commit()
                logger.info(f"✅ Admin user '{admin_username}' created")
        finally:
            db.close()

        logger.info("🎉 Database initialization completed successfully!")
        logger.info("📊 You can now start the application with: python backend/main.py")
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {str(e)}")
        logger.error("💡 Make sure MySQL is running and credentials are correct in .env file")
        sys.exit(1)

if __name__ == "__main__":
    init_database()