"""
Order Schemas for request/response validation
"""

from pydantic import BaseModel, ConfigDict, Field
from typing import List, Optional
from datetime import datetime


class OrderItemCreate(BaseModel):
    """Schema for creating an order item"""
    product_id: int
    quantity: int = Field(gt=0, description="Quantity must be greater than 0")


class OrderItemResponse(BaseModel):
    """Schema for order item in responses"""
    id: int
    product_id: int
    product_name: Optional[str] = None  # From product relationship
    quantity: int
    unit_price: float
    subtotal: Optional[float] = None  # quantity * unit_price
    
    model_config = ConfigDict(from_attributes=True)


class OrderCreate(BaseModel):
    """Schema for creating a new order"""
    # FIX: Changed min_items=1 to min_length=1 and removed the positional '...'
    items: List[OrderItemCreate] = Field(min_length=1, description="Order must have at least 1 item")
    shipping_address: str = Field(min_length=10, max_length=500)


class OrderResponse(BaseModel):
    """Schema for order data in responses"""
    id: int
    user_id: int
    user_email: Optional[str] = None  # From user relationship
    order_date: datetime
    status: str
    total_amount: float
    shipping_address: str
    items: List[OrderItemResponse] = []
    
    model_config = ConfigDict(from_attributes=True)


class OrderStatusUpdate(BaseModel):
    """Schema for updating order status"""
    status: str = Field(description="New status: pending, confirmed, shipped, delivered, cancelled")
