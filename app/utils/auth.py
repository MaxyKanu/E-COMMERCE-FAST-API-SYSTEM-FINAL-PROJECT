"""
JWT Authentication Utilities
Handles token creation and user validation for protected endpoints
"""

from datetime import datetime, timedelta, timezone
from typing import Optional
from jose import JWTError, jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.config import settings
from app.database import get_db
from app.models.user import User
from app.schemas.user import TokenData

# OAuth2 scheme for token extraction
# tokenUrl should match your login endpoint
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token
    
    Args:
        data: Dictionary of claims to encode in token (user_id, email, is_admin)
        expires_delta: Optional custom expiration time, defaults to 30 minutes
    
    Returns:
        str: Encoded JWT token string
    """
    # Copy the data to avoid modifying the original
    to_encode = data.copy()
    
    # Set expiration time using timezone-aware UTC
    now = datetime.now(timezone.utc)
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # Add expiration to token claims (JWT requires a UNIX timestamp int)
    to_encode.update({"exp": int(expire.timestamp())})
    
    # Encode the JWT token
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> User:
    """
    Get the current authenticated user from JWT token
    
    This is the main dependency used to protect endpoints.
    Usage: current_user: User = Depends(get_current_user)
    
    Args:
        token: JWT token extracted from Authorization header
        db: Database session
    
    Returns:
        User: The authenticated user object
    
    Raises:
        HTTPException 401: If token is invalid or expired
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # Decode the JWT token
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        
        # Extract user email from token
        email: Optional[str] = payload.get("email")
        if email is None:
            raise credentials_exception
        
        # Create token data object
        token_data = TokenData(
            email=email,
            user_id=payload.get("user_id"),
            is_admin=payload.get("is_admin", False)
        )
        
    except JWTError:
        raise credentials_exception
    
    # Find user in database
    user = db.query(User).filter(User.email == token_data.email).first()
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Check if the current user is active
    
    Args:
        current_user: User from get_current_user dependency
    
    Returns:
        User: The active user
    
    Raises:
        HTTPException 403: If user account is disabled
    """
    # Safe check using getattr fallback in case is_active isn't configured in your DB model yet
    if not getattr(current_user, "is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled"
        )
    return current_user


async def get_current_admin_user(
    current_user: User = Depends(get_current_active_user)
) -> User:
    """
    Check if the current user has admin privileges
    
    Args:
        current_user: User from get_current_active_user dependency
    
    Returns:
        User: The admin user
    
    Raises:
        HTTPException 403: If user is not an admin
    """
    # Safe check using getattr fallback in case is_admin isn't configured in your DB model yet
    if not getattr(current_user, "is_admin", False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user
