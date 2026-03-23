#!/usr/bin/env python3
"""
Setup script to create initial admin user and update database schema
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from passlib.context import CryptContext

from backend.db.database import engine, SessionLocal
from backend.models.database_models import Base, Admin, User

# Password hashing
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash a password using argon2"""
    return pwd_context.hash(password)

def create_tables():
    """Create all database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")

def create_admin_user(db: Session, email: str, password: str):
    """Create admin user if not exists"""
    # Check if admin already exists
    existing_admin = db.query(Admin).filter(Admin.username == email).first()
    if existing_admin:
        print(f"⚠️  Admin user '{email}' already exists!")
        return existing_admin
    
    # Create new admin
    hashed_password = hash_password(password)
    admin = Admin(
        username=email,
        hashed_password=hashed_password,
        is_active=1
    )
    
    db.add(admin)
    db.commit()
    db.refresh(admin)
    
    print(f"✅ Admin user '{email}' created successfully!")
    return admin

def main():
    """Main setup function"""
    print("🚀 Starting HealthAI Database Setup...")
    
    # Create tables
    create_tables()
    
    # Create admin user
    db = SessionLocal()
    try:
        # You can change these credentials as needed
        admin_email = "admin@healthai.com"  # Replace with your email
        admin_password = "admin123"         # Replace with a secure password
        
        print(f"\n📝 Creating admin user...")
        print(f"   Email: {admin_email}")
        print(f"   Password: {admin_password}")
        print(f"   ⚠️  Please change this password after first login! ⚠️")
        
        create_admin_user(db, admin_email, admin_password)
        
        print(f"\n✅ Setup completed successfully!")
        print(f"\n🔑 Admin Login Credentials:")
        print(f"   Email: {admin_email}")
        print(f"   Password: {admin_password}")
        print(f"   Role: admin (Select 'Medical Staff' during login)")
        print(f"\n🌐 You can now start the server with:")
        print(f"   /home/dev/projects/python/kbsProject/venv/bin/uvicorn backend.main:app --host 0.0.0.0 --port 8000")
        
    except Exception as e:
        print(f"❌ Error during setup: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    main()