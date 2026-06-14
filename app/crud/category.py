"""
Category CRUD Operations
Handles all database operations for the Category model
"""

from sqlalchemy.orm import Session
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryUpdate
from typing import List, Optional


def get_category(db: Session, category_id: int) -> Optional[Category]:
    """
    Get a single category by ID
    
    Args:
        db: Database session
        category_id: Category's ID
    
    Returns:
        Category object if found, None otherwise
    """
    return db.query(Category).filter(Category.id == category_id).first()


def get_categories(db: Session, skip: int = 0, limit: int = 100) -> List[Category]:
    """
    Get all categories with pagination
    
    Args:
        db: Database session
        skip: Number of records to skip
        limit: Maximum number of records
    
    Returns:
        List of Category objects
    """
    return db.query(Category).offset(skip).limit(limit).all()


def create_category(db: Session, category: CategoryCreate) -> Category:
    """
    Create a new category
    
    Args:
        db: Database session
        category: Category creation schema
    
    Returns:
        Created Category object
    """
    db_category = Category(
        name=category.name,
        description=category.description
    )
    
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    
    return db_category


def update_category(db: Session, category_id: int, category_data: CategoryUpdate) -> Optional[Category]:
    """
    Update an existing category
    
    Args:
        db: Database session
        category_id: ID of category to update
        category_data: Schema with fields to update
    
    Returns:
        Updated Category object if found, None otherwise
    """
    db_category = get_category(db, category_id)
    if not db_category:
        return None
    
    # Apply only the fields that were provided
    update_data = category_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_category, field, value)
    
    db.commit()
    db.refresh(db_category)
    
    return db_category


def delete_category(db: Session, category_id: int) -> bool:
    """
    Delete a category by ID
    
    Args:
        db: Database session
        category_id: ID of category to delete
    
    Returns:
        bool: True if deleted, False if not found
    """
    db_category = get_category(db, category_id)
    if not db_category:
        return False
    
    db.delete(db_category)
    db.commit()
    
    return True