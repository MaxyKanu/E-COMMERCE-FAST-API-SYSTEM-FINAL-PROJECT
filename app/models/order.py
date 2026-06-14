"""
Order and OrderItem Models
Handles customer orders and line items
Order creation triggers stock deduction and email notification
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from app.database import Base


class OrderStatus(str, enum.Enum):
    """Valid order statuses for tracking order lifecycle"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class Order(Base):
    """
    Order table representing a customer's purchase
    Contains order-level information and status
    """
    __tablename__ = "orders"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key to user who placed the order
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),  # Delete order if user deleted
        nullable=False
    )
    
    # Order details
    order_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    status = Column(
        Enum(OrderStatus),
        default=OrderStatus.PENDING,
        nullable=False
    )
    total_amount = Column(Float, nullable=False, default=0.0)
    shipping_address = Column(String(500), nullable=False)
    
    # Relationships
    user = relationship(
        "User",
        back_populates="orders",
        lazy="joined"  # Always load user with order
    )
    
    items = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan",  # Delete items when order deleted
        lazy="selectin"  # Efficient loading of multiple items
    )
    
    def __repr__(self) -> str:
        """String representation for debugging"""
        return f"<Order(id={self.id}, status='{self.status}', total={self.total_amount})>"


class OrderItem(Base):
    """
    OrderItem table - individual line items within an order
    Each item links a product with a quantity and price at time of order
    """
    __tablename__ = "order_items"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign keys
    order_id = Column(
        Integer,
        ForeignKey("orders.id", ondelete="CASCADE"),  # Delete item if order deleted
        nullable=False
    )
    product_id = Column(
        Integer,
        ForeignKey("products.id", ondelete="RESTRICT"),  # Prevent deletion if in order
        nullable=False
    )
    
    # Order item details
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)  # Price at time of order (historical record)
    
    # Relationships
    order = relationship(
        "Order",
        back_populates="items",
        lazy="joined"
    )
    
    product = relationship(
        "Product",
        back_populates="order_items",
        lazy="joined"
    )
    
    def __repr__(self) -> str:
        """String representation for debugging"""
        return f"<OrderItem(id={self.id}, order={self.order_id}, product={self.product_id}, qty={self.quantity})>"