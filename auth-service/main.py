import os
import logging
from fastapi import FastAPI, HTTPException, Header
from pydantic import BaseModel
from datetime import datetime, timedelta
import jwt
import bcrypt
from sqlalchemy import create_engine, Column, String, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from contextlib import asynccontextmanager

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://authuser:authpassword123@auth-db:5432/authdb")
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-super-secret-jwt-key-change-in-production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRATION_HOURS = int(os.getenv("JWT_EXPIRATION_HOURS", 24))

# Database Setup
Base = declarative_base()

class User(Base):
    """User model for authentication."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="user", nullable=False)  # "user" or "admin"
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Create engine and session
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Pydantic models
class RegisterRequest(BaseModel):
    email: str
    username: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    username: str
    role: str
    created_at: datetime

# Utility functions
def hash_password(password: str) -> str:
    """Hash password using bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()

def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash."""
    return bcrypt.checkpw(password.encode(), hashed.encode())

def generate_jwt(user_id: int, email: str, role: str) -> str:
    """Generate JWT token."""
    payload = {
        "user_id": user_id,
        "email": email,
        "role": role,
        "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS),
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# FastAPI app
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    # Startup: Create tables
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created/verified")
    except Exception as e:
        logger.error(f"Database initialization error: {str(e)}")
    yield
    logger.info("Auth Service shutdown")

app = FastAPI(title="Auth Service", version="1.0.0", lifespan=lifespan)

# ====================== Health Check ======================

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "auth-service", "timestamp": datetime.utcnow().isoformat()}

# ====================== Auth Endpoints ======================

@app.post("/register")
async def register(req: RegisterRequest, db: Session = None):
    """Register a new user."""
    if db is None:
        db = next(get_db())
    
    try:
        # Check if user exists
        existing_user = db.query(User).filter(
            (User.email == req.email) | (User.username == req.username)
        ).first()
        
        if existing_user:
            raise HTTPException(status_code=409, detail="User already exists")
        
        # Create new user
        hashed_pwd = hash_password(req.password)
        new_user = User(
            email=req.email,
            username=req.username,
            hashed_password=hashed_pwd,
            role="user"  # Default role
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        logger.info(f"User registered: {req.email}")
        
        return {
            "id": new_user.id,
            "email": new_user.email,
            "username": new_user.username,
            "role": new_user.role,
            "message": "User registered successfully"
        }
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"Registration error: {str(e)}")
        raise HTTPException(status_code=500, detail="Registration failed")
    finally:
        db.close()

@app.post("/login")
async def login(req: LoginRequest, db: Session = None):
    """Login user and return JWT token."""
    if db is None:
        db = next(get_db())
    
    try:
        # Find user by email
        user = db.query(User).filter(User.email == req.email).first()
        
        if not user or not verify_password(req.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Generate JWT
        token = generate_jwt(user.id, user.email, user.role)
        
        logger.info(f"User logged in: {req.email}")
        
        return {
            "access_token": token,
            "token_type": "bearer",
            "user_id": user.id,
            "email": user.email,
            "role": user.role
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        raise HTTPException(status_code=500, detail="Login failed")
    finally:
        db.close()

@app.get("/profile")
async def get_profile(x_user_id: str = Header(None), db: Session = None):
    """Get user profile."""
    if db is None:
        db = next(get_db())
    
    try:
        if not x_user_id:
            raise HTTPException(status_code=400, detail="User ID header missing")
        
        user = db.query(User).filter(User.id == int(x_user_id)).first()
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "role": user.role,
            "created_at": user.created_at.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get profile error: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch profile")
    finally:
        db.close()

# ====================== Root Route ======================

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Auth Service",
        "version": "1.0.0",
        "status": "operational"
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("AUTH_SERVICE_PORT", 8001))
    uvicorn.run(app, host="0.0.0.0", port=port)
