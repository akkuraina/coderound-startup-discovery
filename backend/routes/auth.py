from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
import logging
from database import get_db
from models import User
from schemas import UserCreate, UserLogin, UserResponse, Token
from utils.auth import hash_password, verify_password, create_access_token

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/signup", response_model=Token)
async def signup(user: UserCreate, db: Session = Depends(get_db)):
    """
    User signup endpoint
    Creates a new user account with email and password
    """
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == user.email).first()
        if existing_user:
            logger.warning(f"Signup attempt with existing email: {user.email}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Create new user
        # Trim password to 72 bytes (bcrypt limit)
        password = user.password[:72]
        hashed_password = hash_password(password)
        db_user = User(
            email=user.email,
            password_hash=hashed_password,
            name=user.name
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        logger.info(f"New user registered: {user.email}")
        
        # Create token
        access_token = create_access_token(email=user.email)
        user_response = UserResponse.from_orm(db_user)
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user_response
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Signup error: {e}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Signup failed"
        )

@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    User login endpoint
    Authenticates user and returns JWT token
    """
    try:
        # Find user by email
        user = db.query(User).filter(User.email == credentials.email).first()
        
        # Trim password to 72 bytes (bcrypt limit) for verification
        password = credentials.password[:72]
        if not user or not verify_password(password, user.password_hash):
            logger.warning(f"Failed login attempt: {credentials.email}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is inactive"
            )
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.commit()
        
        logger.info(f"User login successful: {user.email}")
        
        # Create token
        access_token = create_access_token(email=user.email)
        user_response = UserResponse.from_orm(user)
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user_response
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Login error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Login failed"
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user(
    token: str = None,
    db: Session = Depends(get_db)
):
    """
    Get current user profile
    Requires valid JWT token
    """
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )
    
    try:
        from utils.auth import decode_token
        email = decode_token(token)
        
        if not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserResponse.from_orm(user)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get current user error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user"
        )

@router.post("/logout")
async def logout():
    """
    User logout endpoint
    Client should delete the token from storage
    """
    return {"message": "Logged out successfully"}
