"""
Category Schemas for request/response validation
"""

from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime


class CategoryBase(BaseModel):
    """Base category fields"""
    name: str = Field(min_length=2, max_length=100)
    description: Optional[str] = None


class CategoryCreate(CategoryBase):
    """Schema for creating a new category"""
    pass


class CategoryUpdate(BaseModel):
    """Schema for updating category - fields optional"""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = None


class CategoryResponse(BaseModel):
    """Schema for category data in responses"""
    id: int
    name: str
    description: Optional[str] = None
    created_at: datetime
    
    # Pydantic v2 configuration - converts ORM objects to Pydantic
    model_config = ConfigDict(from_attributes=True)