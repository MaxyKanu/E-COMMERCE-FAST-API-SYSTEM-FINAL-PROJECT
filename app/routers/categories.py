"""
Categories Router
Handles category listing, creation, updating, and deletion
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse
from app.crud.category import (
    get_category,
    get_categories,
    create_category,
    update_category,
    delete_category
)
from app.utils.auth import get_current_admin_user
from app.models.user import User

router = APIRouter(
    prefix="/categories",
    tags=["Categories"]
)


@router.get(
    "/",
    response_model=List[CategoryResponse],
    status_code=status.HTTP_200_OK,
    summary="List all categories (public)",
    description="Get all product categories. Public endpoint."
)
def list_categories(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List all categories
    
    - Public endpoint
    - Supports pagination
    """
    categories = get_categories(db, skip=skip, limit=limit)
    return categories


@router.get(
    "/{category_id}",
    response_model=CategoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Get category by ID (public)",
    description="Get a specific category by its ID."
)
def read_category(category_id: int, db: Session = Depends(get_db)):
    """
    Get a single category
    
    - Public endpoint
    - Returns 404 if not found
    """
    category = get_category(db, category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    return category


@router.post(
    "/",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create category (admin only)",
    description="Create a new product category. Requires admin privileges."
)
def create_new_category(
    category_data: CategoryCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    Create a new category
    
    - Admin only endpoint
    - Category name must be unique
    """
    category = create_category(db, category_data)
    return category


@router.put(
    "/{category_id}",
    response_model=CategoryResponse,
    status_code=status.HTTP_200_OK,
    summary="Update category (admin only)",
    description="Update an existing category. Requires admin privileges."
)
def update_existing_category(
    category_id: int,
    category_data: CategoryUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    Update an existing category
    
    - Admin only endpoint
    - Only provided fields are updated
    """
    category = update_category(db, category_id, category_data)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    return category


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete category (admin only)",
    description="Delete a category. Requires admin privileges."
)
def delete_existing_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    Delete a category
    
    - Admin only endpoint
    - Returns 204 No Content
    """
    success = delete_category(db, category_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    return None