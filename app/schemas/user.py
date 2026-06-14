"""
User Schemas for request/response validation
Uses Pydantic v2 with model_config instead of old orm_mode
"""

from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """Base user fields shared across schemas"""
    email: EmailStr  # Validates email format automatically
    full_name: str = Field(min_length=2, max_length=255)


class UserCreate(UserBase):
    """Schema for user registration"""
    password: str = Field(min_length=8, max_length=100)  # Will be hashed before storage


class UserUpdate(BaseModel):
    """Schema for updating user - all fields optional"""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    password: Optional[str] = Field(None, min_length=8, max_length=100)
    is_active: Optional[bool] = None
    is_admin: Optional[bool] = None


class UserResponse(BaseModel):
    """Schema for user data in responses - NEVER includes password"""
    id: int
    email: str
    full_name: str
    is_active: bool
    is_admin: bool
    created_at: datetime
    
    # Pydantic v2 configuration - converts ORM objects to Pydantic
    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    """Schema for login credentials"""
    email: EmailStr
    password: str


class Token(BaseModel):
    """JWT token response schema"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Data stored inside JWT token"""
    email: Optional[str] = None
    user_id: Optional[int] = None
    is_admin: Optional[bool] = None