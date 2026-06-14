"""
Review Schemas for request/response validation
"""

from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Optional
from datetime import datetime


class ReviewBase(BaseModel):
    """Base review fields"""
    rating: int = Field(ge=1, le=5, description="Rating must be between 1 and 5")
    comment: Optional[str] = Field(None, max_length=1000)


class ReviewCreate(ReviewBase):
    """Schema for creating a new review"""
    
    @field_validator('rating')
    @classmethod
    def validate_rating(cls, v: int) -> int:
        """Ensure rating is between 1 and 5"""
        if v < 1 or v > 5:
            raise ValueError('Rating must be between 1 and 5')
        return v


class ReviewUpdate(BaseModel):
    """Schema for updating a review"""
    rating: Optional[int] = Field(None, ge=1, le=5)
    comment: Optional[str] = Field(None, max_length=1000)
    
    @field_validator('rating')
    @classmethod
    def validate_rating(cls, v: Optional[int]) -> Optional[int]:
        """Validate rating if provided"""
        if v is not None and (v < 1 or v > 5):
            raise ValueError('Rating must be between 1 and 5')
        return v


class ReviewResponse(BaseModel):
    """Schema for review data in responses"""
    id: int
    product_id: int
    user_id: int
    user_name: Optional[str] = None  # From user relationship
    rating: int
    comment: Optional[str] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)