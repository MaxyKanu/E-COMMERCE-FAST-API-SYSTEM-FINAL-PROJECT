"""
User CRUD Operations
Handles all database operations for the User model
"""

from sqlalchemy.orm import Session
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.utils.hashing import get_password_hash
from typing import List, Optional


def get_user(db: Session, user_id: int) -> Optional[User]:
    """
    Get a single user by ID
    
    Args:
        db: Database session
        user_id: User's ID
    
    Returns:
        User object if found, None otherwise
    """
    return db.query(User).filter(User.id == user_id).first()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """
    Get a user by their email address
    Used during login and registration to check duplicates
    
    Args:
        db: Database session
        email: User's email address
    
    Returns:
        User object if found, None otherwise
    """
    return db.query(User).filter(User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
    """
    Get a list of users with pagination
    
    Args:
        db: Database session
        skip: Number of records to skip (for pagination)
        limit: Maximum number of records to return
    
    Returns:
        List of User objects
    """
    return db.query(User).offset(skip).limit(limit).all()


def create_user(db: Session, user: UserCreate) -> User:
    """
    Create a new user with hashed password
    
    Args:
        db: Database session
        user: User creation schema with email, name, password
    
    Returns:
        Created User object
    """
    # Hash the password before storing (NEVER store plain text)
    hashed_password = get_password_hash(user.password)
    
    # Create user object
    db_user = User(
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name,
        is_active=True,
        is_admin=False  # New users are never admins by default
    )
    
    # Save to database
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user


def update_user(db: Session, user_id: int, user_data: UserUpdate) -> Optional[User]:
    """
    Update an existing user's information
    
    Args:
        db: Database session
        user_id: ID of user to update
        user_data: Schema with fields to update
    
    Returns:
        Updated User object if found, None otherwise
    """
    db_user = get_user(db, user_id)
    if not db_user:
        return None
    
    # Convert update data to dict, excluding None values
    update_data = user_data.model_dump(exclude_unset=True)
    
    # If password is being updated, hash it first
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    
    # Apply updates
    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.commit()
    db.refresh(db_user)
    
    return db_user


def delete_user(db: Session, user_id: int) -> bool:
    """
    Delete a user by ID
    
    Args:
        db: Database session
        user_id: ID of user to delete
    
    Returns:
        bool: True if deleted, False if user not found
    """
    db_user = get_user(db, user_id)
    if not db_user:
        return False
    
    db.delete(db_user)
    db.commit()
    
    return True