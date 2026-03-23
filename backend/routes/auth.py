from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from passlib.context import CryptContext
import re

from backend.db.database import get_db
from backend.models.database_models import User, Admin
from backend.models.pydantic_models import UserLogin, UserRegister, AuthResponse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBearer()
pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")

def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_password(password: str) -> bool:
    """Validate password strength"""
    if len(password) < 6:
        return False
    return True

@router.post("/register", response_model=AuthResponse)
async def register_user(user_data: UserRegister, db: Session = Depends(get_db)):
    """Register a new user - patients only (admin already exists)"""
    try:
        # Validate email format
        if not validate_email(user_data.email):
            raise HTTPException(status_code=400, detail="Invalid email format")
        
        # Validate password strength
        if not validate_password(user_data.password):
            raise HTTPException(status_code=400, detail="Password must be at least 6 characters long")

        # (argon2 used) no bcrypt 72-byte limitation; continue
        
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user_data.email.lower()).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Check if email exists in admin table (admin shouldn't register as user)
        existing_admin = db.query(Admin).filter(Admin.username == user_data.email.lower()).first()
        if existing_admin:
            raise HTTPException(status_code=400, detail="This email is reserved for admin access")
        
        # Create new user
        full_name = f"{user_data.first_name} {user_data.last_name}"
        hashed_password = hash_password(user_data.password)
        
        new_user = User(
            email=user_data.email.lower(),
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            name=full_name,
            age=user_data.age,
            gender=user_data.gender,
            phone=user_data.phone,
            hashed_password=hashed_password,
            is_active=1,
            role="user"
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        logger.info(f"New user registered: {user_data.email}")
        
        return AuthResponse(
            success=True,
            message="Account created successfully! Welcome to HealthAI.",
            user={
                "id": new_user.id,
                "email": new_user.email,
                "name": new_user.name,
                "firstName": new_user.first_name,
                "lastName": new_user.last_name,
                "age": new_user.age,
                "gender": new_user.gender,
                "phone": new_user.phone
            },
            role="user"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Registration failed. Please try again.")

@router.post("/login", response_model=AuthResponse)
async def login_user(login_data: UserLogin, db: Session = Depends(get_db)):
    """Login user or admin with database validation"""
    try:
        # Validate email format
        if not validate_email(login_data.email):
            raise HTTPException(status_code=400, detail="Invalid email format")
        
        email = login_data.email.lower()
        
        # (argon2 used) no bcrypt 72-byte limitation; continue

        if login_data.role == "admin":
            # Check admin login
            admin = db.query(Admin).filter(
                Admin.username == email,
                Admin.is_active == 1
            ).first()
            
            if not admin or not verify_password(login_data.password, admin.hashed_password):
                raise HTTPException(status_code=401, detail="Invalid admin credentials")
            
            logger.info(f"Admin login successful: {email}")
            
            return AuthResponse(
                success=True,
                message="Admin login successful! Welcome to the management console.",
                user={
                    "id": admin.id,
                    "email": admin.username,
                    "name": "Administrator",
                    "firstName": "Admin",
                    "role": "admin"
                },
                role="admin"
            )
            
        else:  # user role
            # Check regular user login
            user = db.query(User).filter(
                User.email == email,
                User.is_active == 1
            ).first()
            
            if not user or not verify_password(login_data.password, user.hashed_password):
                raise HTTPException(status_code=401, detail="Invalid user credentials")
            
            logger.info(f"User login successful: {email}")
            
            return AuthResponse(
                success=True,
                message="Login successful! Welcome back to HealthAI.",
                user={
                    "id": user.id,
                    "email": user.email,
                    "name": user.name,
                    "firstName": user.first_name,
                    "lastName": user.last_name,
                    "age": user.age,
                    "gender": user.gender,
                    "phone": user.phone
                },
                role="user"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(status_code=500, detail="Login failed. Please try again.")

@router.get("/validate-token")
async def validate_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Validate authentication token (for future JWT implementation)"""
    # For now, return basic validation
    # In production, implement proper JWT token validation
    return {"valid": True, "message": "Token validation not implemented yet"}