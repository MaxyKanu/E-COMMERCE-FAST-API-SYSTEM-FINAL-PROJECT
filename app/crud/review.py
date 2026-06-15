"""
Review CRUD Operations
Handles all database operations for the Review model
"""

from sqlalchemy.orm import Session
from app.models.review import Review
from app.schemas.review import ReviewCreate, ReviewUpdate
from typing import List, Optional
from fastapi import HTTPException, status


def create_review(
    db: Session,
    review_data: ReviewCreate,
    product_id: int,
    user_id: int
) -> Review:
    """
    Create a new product review
    
    Args:
        db: Database session
        review_data: Review creation schema
        product_id: ID of the product being reviewed
        user_id: ID of the user writing the review
    
    Returns:
        Created Review object
    """
    # Check if user already reviewed this product
    existing = (
        db.query(Review)
        .filter(
            Review.product_id == product_id,
            Review.user_id == user_id
        )
        .first()
    )
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already reviewed this product"
        )
    
    db_review = Review(
        product_id=product_id,
        user_id=user_id,
        rating=review_data.rating,
        comment=review_data.comment
    )
    
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    
    return db_review


def get_product_reviews(db: Session, product_id: int) -> List[Review]:
    """
    Get all reviews for a specific product
    
    Args:
        db: Database session
        product_id: ID of the product
    
    Returns:
        List of Review objects
    """
    return (
        db.query(Review)
        .filter(Review.product_id == product_id)
        .order_by(Review.created_at.desc())
        .all()
    )


def get_review(db: Session, review_id: int) -> Optional[Review]:
    """
    Get a single review by ID
    
    Args:
        db: Database session
        review_id: Review's ID
    
    Returns:
        Review object if found, None otherwise
    """
    return db.query(Review).filter(Review.id == review_id).first()


def update_review(db: Session, review_id: int, review_data: ReviewUpdate) -> Optional[Review]:
    """
    Update an existing review
    
    Args:
        db: Database session
        review_id: ID of review to update
        review_data: Schema with fields to update
    
    Returns:
        Updated Review object if found, None otherwise
    """
    db_review = get_review(db, review_id)
    if not db_review:
        return None
    
    update_data = review_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_review, field, value)
    
    db.commit()
    db.refresh(db_review)
    
    return db_review


def delete_review(db: Session, review_id: int) -> bool:
    """
    Delete a review by ID
    
    Args:
        db: Database session
        review_id: ID of review to delete
    
    Returns:
        bool: True if deleted, False if not found
    """
    db_review = get_review(db, review_id)
    if not db_review:
        return False
    
    db.delete(db_review)
    db.commit()
    
    return True