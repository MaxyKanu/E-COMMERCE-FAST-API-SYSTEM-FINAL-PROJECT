"""
Product Model
Core inventory item with price, stock, and category
Represents actual goods sold by Sierra Leone businesses
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Product(Base):
    """
    Product table - the main inventory items
    Tracks stock quantity in real-time for accurate inventory management
    """
    __tablename__ = "products"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Product details
    name = Column(String(255), index=True, nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    stock_quantity = Column(Integer, nullable=False, default=0)
    
    # Foreign key to category
    category_id = Column(
        Integer,
        ForeignKey("categories.id", ondelete="SET NULL"),  # Keep product if category deleted
        nullable=True
    )
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),  # Auto-update when product is modified
        nullable=False
    )
    
    # Relationships
    category = relationship(
        "Category",
        back_populates="products",
        lazy="joined"  # Always load category with product
    )
    
    order_items = relationship(
        "OrderItem",
        back_populates="product",
        lazy="select"
    )
    
    reviews = relationship(
        "Review",
        back_populates="product",
        cascade="all, delete-orphan",
        lazy="select"
    )
    
    def __repr__(self) -> str:
        """String representation for debugging"""
        return f"<Product(id={self.id}, name='{self.name}', price={self.price}, stock={self.stock_quantity})>"