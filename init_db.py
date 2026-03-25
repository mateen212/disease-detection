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
from passlib.hash import argon2
from sqlalchemy import inspect
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

        # Ensure `hashed_password` column exists on `users` table, then seed initial admin and a sample user
        inspector = inspect(engine)
        users_columns = [c['name'] for c in inspector.get_columns('users')] if 'users' in inspector.get_table_names() else []
        if 'hashed_password' not in users_columns:
            logger.info("➕ Adding 'hashed_password' column to 'users' table...")
            with engine.connect() as conn:
                conn.execute(text("ALTER TABLE users ADD COLUMN hashed_password VARCHAR(255) NULL"))
            logger.info("✅ 'hashed_password' column added to 'users'")

        logger.info("🔐 Ensuring admin user exists...")
        db = SessionLocal()
        try:
            existing = db.query(Admin).filter(Admin.username == admin_username).first()
            if existing:
                logger.info(f"ℹ️ Admin user '{admin_username}' already exists (id={existing.id})")
            else:
                hashed = argon2.hash(admin_password)
                admin = Admin(username=admin_username, hashed_password=hashed, is_active=1)
                db.add(admin)
                db.commit()
                logger.info(f"✅ Admin user '{admin_username}' created")
            
            # Seed a sample normal user if not exists
            user_username = os.getenv("USER_USERNAME", "user")
            user_password = os.getenv("USER_PASSWORD", "userpass")
            # import here to avoid circular imports at module import time
            from backend.models.database_models import User
            existing_user = db.query(User).filter(User.name == user_username).first()
            if existing_user:
                # ensure hashed_password present
                if not existing_user.hashed_password:
                    existing_user.hashed_password = argon2.hash(user_password)
                    db.add(existing_user)
                    db.commit()
                    logger.info(f"✅ Updated password for existing user '{user_username}'")
                else:
                    logger.info(f"ℹ️ User '{user_username}' already exists (id={existing_user.id})")
            else:
                hashed_user_pw = argon2.hash(user_password)
                # Provide required non-null fields defined by the User model
                new_user = User(
                    email=f"{user_username}@example.com",
                    first_name="Sample",
                    last_name="User",
                    name=user_username,
                    age=30,
                    gender='other',
                    hashed_password=hashed_user_pw,
                    is_active=1,
                    role='user'
                )
                db.add(new_user)
                db.commit()
                logger.info(f"✅ Sample user '{user_username}' created (id={new_user.id})")
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