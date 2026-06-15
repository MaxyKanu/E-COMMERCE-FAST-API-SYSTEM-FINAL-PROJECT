"""
Users Router
Handles user management (admin operations and self-service)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.user import UserResponse, UserUpdate
from app.crud.user import get_user, get_users, update_user, delete_user
from app.utils.auth import get_current_active_user, get_current_admin_user
from app.models.user import User

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.get(
    "/",
    response_model=List[UserResponse],
    status_code=status.HTTP_200_OK,
    summary="List all users (admin only)",
    description="Get all registered users. Requires admin privileges."
)
def list_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    List all users
    
    - Admin only endpoint
    - Supports pagination
    """
    users = get_users(db, skip=skip, limit=limit)
    return users


@router.get(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Get user by ID (admin or self)",
    description="Get a specific user. Admins can view any user, regular users can only view themselves."
)
def read_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a single user by ID
    
    - Admin: Can view any user
    - Regular user: Can only view their own profile
    """
    # FIX 1 & 2: Added type ignore for column boolean evaluation and ID comparison
    if not current_user.is_admin and current_user.id != user_id:  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own profile"
        )
    
    user = get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.put(
    "/{user_id}",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Update user (admin or self)",
    description="Update user information. Admins can update any user, regular users can only update themselves."
)
def update_existing_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update a user
    
    - Admin: Can update any user (including making others admin)
    - Regular user: Can only update their own profile
    - Regular users cannot change their is_admin status
    """
    # FIX 3 & 4: Added type ignore for column boolean evaluation and ID comparison
    if not current_user.is_admin and current_user.id != user_id:  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own profile"
        )
    
    # FIX 5: Added type ignore for checking column boolean truthiness
    if not current_user.is_admin and user_data.is_admin is not None:  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can change admin status"
        )
    
    user = update_user(db, user_id, user_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user


@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete user (admin only)",
    description="Delete a user account. Requires admin privileges."
)
def delete_existing_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    Delete a user
    
    - Admin only endpoint
    - Cannot delete yourself
    """
    # FIX 6: Added type ignore for comparing Admin ID column to function parameter
    if current_admin.id == user_id:  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot delete your own admin account"
        )
    
    success = delete_user(db, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return None
