"""
Review Model
Customer product reviews with ratings (1-5)
Enables feedback and quality tracking for Sierra Leone businesses
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Review(Base):
    """
    Review table for product feedback
    Rating must be between 1 and 5 (enforced by database constraint)
    """
    __tablename__ = "reviews"
    
    # Add table-level constraint for rating range
    __table_args__ = (
        CheckConstraint(
            "rating >= 1 AND rating <= 5",
            name="ck_review_rating_range"
        ),
    )

    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign keys
    product_id = Column(
        Integer,
        ForeignKey("products.id", ondelete="CASCADE"),  # Delete reviews if product deleted
        nullable=False
    )
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),  # Delete reviews if user deleted
        nullable=False
    )
    
    # Review details
    rating = Column(Integer, nullable=False)  # 1-5 rating enforced by constraint
    comment = Column(String(1000), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    product = relationship(
        "Product",
        back_populates="reviews",
        lazy="joined"
    )
    
    user = relationship(
        "User",
        back_populates="reviews",
        lazy="joined"
    )
    
    def __repr__(self) -> str:
        """String representation for debugging"""
        return f"<Review(id={self.id}, product={self.product_id}, rating={self.rating})>"