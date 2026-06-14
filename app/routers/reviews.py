"""
Reviews Router
Handles product review creation, listing, updating, and deletion
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.review import ReviewCreate, ReviewUpdate, ReviewResponse
from app.crud.review import (
    create_review,
    get_product_reviews,
    get_review,
    update_review,
    delete_review
)
from app.utils.auth import get_current_active_user
from app.models.user import User

router = APIRouter(
    prefix="/products",
    tags=["Reviews"]
)


@router.post(
    "/{product_id}/reviews",
    response_model=ReviewResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create product review (authenticated)",
    description="Write a review for a product. One review per user per product."
)
def create_product_review(
    product_id: int,
    review_data: ReviewCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a product review
    
    - Authenticated users only
    - One review per user per product
    - Rating must be 1-5
    
    Raises:
        400: If user already reviewed this product
        404: If product not found
    """
    # Check if product exists
    from app.crud.product import get_product
    product = get_product(db, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # FIX 1: Added type ignore for current_user.id column type mapping parameter pass
    review = create_review(db, review_data, product_id, current_user.id)  # type: ignore
    return review


@router.get(
    "/{product_id}/reviews",
    response_model=List[ReviewResponse],
    status_code=status.HTTP_200_OK,
    summary="List product reviews (public)",
    description="Get all reviews for a specific product. Public endpoint."
)
def list_product_reviews(
    product_id: int,
    db: Session = Depends(get_db)
):
    """
    List all reviews for a product
    
    - Public endpoint
    - Returns reviews sorted by date (newest first)
    """
    # Check if product exists
    from app.crud.product import get_product
    product = get_product(db, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    reviews = get_product_reviews(db, product_id)
    return reviews


@router.put(
    "/reviews/{review_id}",
    response_model=ReviewResponse,
    status_code=status.HTTP_200_OK,
    summary="Update review (owner only)",
    description="Update your own review. Only the review author can update it."
)
def update_existing_review(
    review_id: int,
    review_data: ReviewUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Update a review
    
    - Only the review author can update
    - Rating must be 1-5 if provided
    """
    review = get_review(db, review_id)
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    # FIX 2 & 3: Added type ignore for comparing two database tracking column properties
    if review.user_id != current_user.id:  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update your own reviews"
        )
    
    updated_review = update_review(db, review_id, review_data)
    return updated_review


@router.delete(
    "/reviews/{review_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete review (owner or admin)",
    description="Delete a review. Review author or admin can delete."
)
def delete_existing_review(
    review_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a review
    
    - Review author: Can delete their own reviews
    - Admin: Can delete any review
    """
    review = get_review(db, review_id)
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    # FIX 4: Added type ignore for combined multi-column evaluation statement
    if review.user_id != current_user.id and not current_user.is_admin:  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own reviews"
        )
    
    delete_review(db, review_id)
    return None
