"""
Password Hashing Utilities
Uses bcrypt - industry standard for password hashing
NEVER store plain text passwords
"""

from passlib.context import CryptContext
from sqlalchemy.orm import Session
from app.models.user import User
from typing import Optional

# Configure bcrypt as the hashing algorithm
# schemes=["bcrypt"]: Use bcrypt for hashing
# deprecated="auto": Automatically upgrade old hashes
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plain text password against its bcrypt hash
    
    Args:
        plain_password: The password to check (from login form)
        hashed_password: The bcrypt hash from database
    
    Returns:
        bool: True if password matches, False otherwise
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt before storing in database
    
    Args:
        password: Plain text password to hash
    
    Returns:
        str: Bcrypt hashed password (ready for database storage)
    """
    return pwd_context.hash(password)


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """
    Authenticate a user by email and password
    
    Args:
        db: Database session
        email: User's email address
        password: Plain text password to verify
    
    Returns:
        User object if authentication successful, None if failed
    """
    # Find user by email
    user = db.query(User).filter(User.email == email).first()
    
    # Check if user exists. (getattr safe fallback in case is_active isn't in your User model yet)
    if not user or not getattr(user, "is_active", True):
        return None
    
    # Verify password against stored hash - wrapped in str() to satisfy Pylance/VS Code
    if not verify_password(password, str(user.hashed_password)):
        return None
    
    return user
