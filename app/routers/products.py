"""
Products Router
Handles product listing, creation, updating, and stock management
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.database import get_db
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse, StockUpdate
from app.crud.product import (
    get_product,
    get_products,
    create_product,
    update_product,
    delete_product,
    update_stock
)
from app.utils.auth import get_current_admin_user
from app.models.user import User

router = APIRouter(
    prefix="/products",
    tags=["Products"]
)


@router.get(
    "/",
    response_model=List[ProductResponse],
    status_code=status.HTTP_200_OK,
    summary="List all products (public)",
    description="Get a paginated list of products with optional search and category filter. Public endpoint."
)
def list_products(
    skip: int = Query(0, ge=0, description="Number of products to skip"),
    limit: int = Query(10, ge=1, le=100, description="Maximum products to return"),
    search: Optional[str] = Query(None, description="Search by product name or description"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    db: Session = Depends(get_db)
):
    """
    List products with pagination and filtering
    
    - Public endpoint (no authentication required)
    - Supports search by name/description
    - Supports filtering by category
    - Default: 10 products per page
    """
    products = get_products(
        db,
        skip=skip,
        limit=limit,
        search=search,
        category_id=category_id
    )
    return products


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
    status_code=status.HTTP_200_OK,
    summary="Get product by ID (public)",
    description="Get detailed information about a specific product."
)
def read_product(product_id: int, db: Session = Depends(get_db)):
    """
    Get a single product by ID
    
    - Public endpoint
    - Returns 404 if product not found
    """
    product = get_product(db, product_id)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return product


@router.post(
    "/",
    response_model=ProductResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create product (admin only)",
    description="Create a new product. Requires admin privileges."
)
def create_new_product(
    product_data: ProductCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    Create a new product
    
    - Admin only endpoint
    - Returns created product with 201 status
    """
    product = create_product(db, product_data)
    return product


@router.put(
    "/{product_id}",
    response_model=ProductResponse,
    status_code=status.HTTP_200_OK,
    summary="Update product (admin only)",
    description="Update an existing product. Requires admin privileges."
)
def update_existing_product(
    product_id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    Update an existing product
    
    - Admin only endpoint
    - Only provided fields are updated
    - Returns 404 if product not found
    """
    product = update_product(db, product_id, product_data)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return product


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete product (admin only)",
    description="Delete a product. Requires admin privileges."
)
def delete_existing_product(
    product_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    Delete a product
    
    - Admin only endpoint
    - Returns 204 No Content on success
    - Returns 404 if product not found
    """
    success = delete_product(db, product_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return None


@router.patch(
    "/{product_id}/stock",
    response_model=ProductResponse,
    status_code=status.HTTP_200_OK,
    summary="Update product stock (admin only)",
    description="Update only the stock quantity of a product. Requires admin privileges."
)
def update_product_stock(
    product_id: int,
    stock_data: StockUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin_user)
):
    """
    Update product stock quantity
    
    - Admin only endpoint
    - Sets absolute stock quantity (not relative)
    - Returns updated product
    """
    product = update_stock(db, product_id, stock_data.quantity)
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return product