"""
User Model
Represents users/customers in the system
Has relationships to orders and reviews
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    """
    User table storing all registered users
    Admins can manage inventory; regular users can place orders
    """
    __tablename__ = "users"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # User credentials and info
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    
    # Account status
    is_active = Column(Boolean, default=True, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    # One user can have many orders
    orders = relationship(
        "Order",
        back_populates="user",
        cascade="all, delete-orphan",  # Delete orders when user is deleted
        lazy="select"  # Load orders on demand
    )
    
    # One user can write many reviews
    reviews = relationship(
        "Review",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="select"
    )
    
    def __repr__(self) -> str:
        """String representation for debugging"""
        return f"<User(id={self.id}, email='{self.email}', is_admin={self.is_admin})>"