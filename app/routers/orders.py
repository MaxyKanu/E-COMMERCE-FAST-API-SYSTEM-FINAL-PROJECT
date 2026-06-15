"""
Orders Router
Handles order creation, retrieval, and status management
Includes async email notification after order creation
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.schemas.order import OrderCreate, OrderResponse, OrderStatusUpdate
from app.crud.order import (
    create_order,
    get_order,
    get_user_orders,
    get_all_orders,
    update_order_status,
    cancel_order
)
from app.utils.auth import get_current_active_user, get_current_admin_user
from app.models.user import User
from app.utils.email import send_order_confirmation

router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)


@router.post(
    "/",
    response_model=OrderResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new order (authenticated)",
    description="Place a new order. Validates stock, deducts inventory, and sends confirmation email."
)
async def create_new_order(
    order_data: OrderCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Create a new order
    
    - Authenticated users only
    - Validates stock availability for all items
    - Deducts stock from inventory
    - Calculates total amount automatically
    - Sends async email confirmation
    
    Raises:
        400: If stock insufficient
        404: If product not found
    """
    # FIX 1: Added type ignore for current_user.id parameter tracking
    order = create_order(db, order_data, current_user.id)  # type: ignore
    
        # Send async order confirmation email
    # This satisfies the async/await requirement
    await send_order_confirmation(order.id, current_user.email)  # type: ignore
    
    return order



@router.get(
    "/my-orders",
    response_model=List[OrderResponse],
    status_code=status.HTTP_200_OK,
    summary="Get my orders (authenticated)",
    description="Get all orders for the currently authenticated user."
)
def get_my_orders(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user's orders
    
    - Authenticated users only
    - Returns orders sorted by date (newest first)
    """
    # FIX 2: Added type ignore for current_user.id parameter tracking
    orders = get_user_orders(db, current_user.id)  # type: ignore
    return orders


@router.get(
    "/{order_id}",
    response_model=OrderResponse,
    status_code=status.HTTP_200_OK,
    summary="Get order by ID (owner or admin)",
    description="Get a specific order. Users can only view their own orders, admins can view any."
)
def read_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a single order by ID
    
    - Users: Can only view their own orders
    - Admin: Can view any order
    """
    order = get_order(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # FIX 3: Added type ignore for multi-column conditional identity statement evaluation
    if not current_user.is_admin and order.user_id != current_user.id:  # type: ignore
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own orders"
        )
    
    return order


@router.put(
    "/{order_id}/status",
    response_model=OrderResponse,
    status_code=status.HTTP_200_OK,
    summary="Update order status (admin only)",
    description="Update the status of an order. Cancelling restores stock. Requires admin privileges."
)
def update_order_status_endpoint(
    order_id: int,
    status_data: OrderStatusUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    Update order status
    
    - Admin only endpoint
    - Cancelling an order restores stock to inventory
    - Valid statuses: pending, confirmed, shipped, delivered, cancelled
    """
    order = update_order_status(db, order_id, status_data.status)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    return order
