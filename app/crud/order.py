"""
Order CRUD Operations
Handles all database operations for Order and OrderItem models
Includes stock validation, automatic total calculation, and stock deduction
"""

from sqlalchemy.orm import Session
from app.models.order import Order, OrderItem, OrderStatus
from app.models.product import Product
from app.schemas.order import OrderCreate, OrderStatusUpdate
from typing import List, Optional
from fastapi import HTTPException, status


def create_order(db: Session, order_data: OrderCreate, user_id: int) -> Order:
    """
    Create a new order with stock validation and deduction
    
    Args:
        db: Database session
        order_data: Order creation schema with items and shipping
        user_id: ID of the user placing the order
    
    Returns:
        Created Order object with items
    
    Raises:
        HTTPException 400: If stock is insufficient for any item
    """
    # Validate all items and calculate total
    total_amount = 0.0
    order_items_data = []
    
    for item_data in order_data.items:
        # Get product from database
        product = db.query(Product).filter(Product.id == item_data.product_id).first()
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Product with ID {item_data.product_id} not found"
            )
        
        # FIX 1: Extract to int to satisfy Pylance conditional operand checker
        available_stock: int = product.stock_quantity  # type: ignore
        
        # Check if enough stock is available using standard int comparison
        if available_stock < item_data.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Insufficient stock for '{product.name}'. "
                       f"Available: {product.stock_quantity}, Requested: {item_data.quantity}"
            )
        
        # Calculate item subtotal
        item_total = product.price * item_data.quantity
        total_amount += item_total
        
        # Store item data for later creation
        order_items_data.append({
            "product": product,
            "quantity": item_data.quantity,
            "unit_price": product.price
        })
    
    # Create the order
    db_order = Order(
        user_id=user_id,
        status=OrderStatus.PENDING,
        total_amount=total_amount,
        shipping_address=order_data.shipping_address
    )
    
    db.add(db_order)
    db.flush()  # Flush to get order.id before creating items
    
    # Create order items and deduct stock
    for item_info in order_items_data:
        # Create order item
        db_item = OrderItem(
            order_id=db_order.id,
            product_id=item_info["product"].id,
            quantity=item_info["quantity"],
            unit_price=item_info["unit_price"]
        )
        db.add(db_item)
        
        # FIX 2: Added type ignore for Column inline subtraction
        item_info["product"].stock_quantity -= item_info["quantity"]  # type: ignore
    
    db.commit()
    db.refresh(db_order)
    
    return db_order


def get_order(db: Session, order_id: int) -> Optional[Order]:
    """
    Get a single order by ID with items
    
    Args:
        db: Database session
        order_id: Order's ID
    
    Returns:
        Order object if found, None otherwise
    """
    return db.query(Order).filter(Order.id == order_id).first()


def get_user_orders(db: Session, user_id: int) -> List[Order]:
    """
    Get all orders for a specific user
    
    Args:
        db: Database session
        user_id: ID of the user
    
    Returns:
        List of Order objects for that user
    """
    return (
        db.query(Order)
        .filter(Order.user_id == user_id)
        .order_by(Order.order_date.desc())
        .all()
    )


def get_all_orders(db: Session, skip: int = 0, limit: int = 100) -> List[Order]:
    """
    Get all orders with pagination (admin only)
    
    Args:
        db: Database session
        skip: Records to skip
        limit: Maximum records
    
    Returns:
        List of Order objects
    """
    return (
        db.query(Order)
        .order_by(Order.order_date.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def update_order_status(db: Session, order_id: int, status_str: str) -> Optional[Order]:
    """
    Update the status of an order
    
    Args:
        db: Database session
        order_id: ID of the order
        status_str: New status string
    
    Returns:
        Updated Order object if found, None otherwise
    """
    db_order = get_order(db, order_id)
    if not db_order:
        return None
    
    # Validate status
    try:
        new_status = OrderStatus(status_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status '{status_str}'. "
                   f"Valid statuses: {[s.value for s in OrderStatus]}"
        )
    
    # FIX 3: Added type ignore for Enum vs Column identity tracking evaluation
    if new_status == OrderStatus.CANCELLED and db_order.status != OrderStatus.CANCELLED:  # type: ignore
        _restore_stock_from_order(db, db_order)
    
    db_order.status = new_status  # type: ignore
    db.commit()
    db.refresh(db_order)
    
    return db_order


def cancel_order(db: Session, order_id: int) -> Optional[Order]:
    """
    Cancel an order and restore stock
    
    Args:
        db: Database session
        order_id: ID of the order to cancel
    
    Returns:
        Cancelled Order object if found, None otherwise
    """
    db_order = get_order(db, order_id)
    if not db_order:
        return None
    
    # FIX 4: Added type ignore for inline column status equality validation
    if db_order.status == OrderStatus.CANCELLED:  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Order is already cancelled"
        )
    
    # Restore stock for all items
    _restore_stock_from_order(db, db_order)
    
    db_order.status = OrderStatus.CANCELLED  # type: ignore
    db.commit()
    db.refresh(db_order)
    
    return db_order


def _restore_stock_from_order(db: Session, order: Order) -> None:
    """
    Helper function to restore stock when an order is cancelled
    
    Args:
        db: Database session
        order: Order object to restore stock from
    """
    for item in order.items:
        product = item.product
        # FIX 5: Added type ignore for tracking Column inline addition math operation
        product.stock_quantity += item.quantity  # type: ignore
