"""
Category Model
Organizes products into groups (Electronics, Clothing, etc.)
Essential for inventory organization
"""

from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Category(Base):
    """
    Category table for product organization
    Each category can contain multiple products
    """
    __tablename__ = "categories"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Category details
    name = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    # One category can have many products
    products = relationship(
        "Product",
        back_populates="category",
        lazy="select"  # Load products when accessed
    )
    
    def __repr__(self) -> str:
        """String representation for debugging"""
        return f"<Category(id={self.id}, name='{self.name}')>"