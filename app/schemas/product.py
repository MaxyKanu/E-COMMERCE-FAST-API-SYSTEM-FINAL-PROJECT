"""
Product Schemas for request/response validation
"""

from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime


class ProductBase(BaseModel):
    """Base product fields"""
    name: str = Field(min_length=2, max_length=255)
    description: Optional[str] = None
    price: float = Field(gt=0, description="Price must be greater than 0")
    stock_quantity: int = Field(ge=0, description="Stock cannot be negative")
    category_id: Optional[int] = None


class ProductCreate(ProductBase):
    """Schema for creating a new product"""
    pass


class ProductUpdate(BaseModel):
    """Schema for updating product - fields optional"""
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    stock_quantity: Optional[int] = Field(None, ge=0)
    category_id: Optional[int] = None


class StockUpdate(BaseModel):
    """Schema for updating only stock quantity"""
    quantity: int = Field(ge=0, description="New stock quantity (cannot be negative)")


class ProductResponse(BaseModel):
    """Schema for product data in responses - includes category name"""
    id: int
    name: str
    description: Optional[str] = None
    price: float
    stock_quantity: int
    category_id: Optional[int] = None
    category_name: Optional[str] = None  # Derived from relationship
    created_at: datetime
    updated_at: datetime
    
    # Pydantic v2 configuration - converts ORM objects to Pydantic
    model_config = ConfigDict(from_attributes=True)
    
    # This validator extracts category name from the relationship
    @classmethod
    def from_orm_with_category(cls, obj):
        """Helper to populate category_name from relationship"""
        data = cls.model_validate(obj).model_dump()
        if obj.category:
            data['category_name'] = obj.category.name
        return cls(**data)