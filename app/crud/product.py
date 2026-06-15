"""
Product CRUD Operations
Handles all database operations for the Product model
"""

from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate
from typing import List, Optional


def get_product(db: Session, product_id: int) -> Optional[Product]:
    """
    Get a single product by ID
    
    Args:
        db: Database session
        product_id: Product's ID
    
    Returns:
        Product object if found, None otherwise
    """
    return db.query(Product).filter(Product.id == product_id).first()


def get_products(
    db: Session,
    skip: int = 0,
    limit: int = 10,
    search: Optional[str] = None,
    category_id: Optional[int] = None
) -> List[Product]:
    """
    Get products with filtering, search, and pagination
    
    Args:
        db: Database session
        skip: Number of records to skip (pagination offset)
        limit: Maximum number of records (page size)
        search: Optional search term (searches name and description)
        category_id: Optional filter by category
    
    Returns:
        List of Product objects matching criteria
    """
    query = db.query(Product)
    
    # Apply search filter if provided
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Product.name.ilike(search_term),
                Product.description.ilike(search_term)
            )
        )
    
    # Apply category filter if provided
    if category_id is not None:
        query = query.filter(Product.category_id == category_id)
    
    # Apply pagination
    return query.offset(skip).limit(limit).all()


def create_product(db: Session, product: ProductCreate) -> Product:
    """
    Create a new product
    
    Args:
        db: Database session
        product: Product creation schema
    
    Returns:
        Created Product object
    """
    db_product = Product(
        name=product.name,
        description=product.description,
        price=product.price,
        stock_quantity=product.stock_quantity,
        category_id=product.category_id
    )
    
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    
    return db_product


def update_product(db: Session, product_id: int, product_data: ProductUpdate) -> Optional[Product]:
    """
    Update an existing product
    
    Args:
        db: Database session
        product_id: ID of product to update
        product_data: Schema with fields to update
    
    Returns:
        Updated Product object if found, None otherwise
    """
    db_product = get_product(db, product_id)
    if not db_product:
        return None
    
    update_data = product_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_product, field, value)
    
    db.commit()
    db.refresh(db_product)
    
    return db_product


def delete_product(db: Session, product_id: int) -> bool:
    """
    Delete a product by ID
    
    Args:
        db: Database session
        product_id: ID of product to delete
    
    Returns:
        bool: True if deleted, False if not found
    """
    db_product = get_product(db, product_id)
    if not db_product:
        return False
    
    db.delete(db_product)
    db.commit()
    
    return True


def update_stock(db: Session, product_id: int, quantity: int) -> Optional[Product]:
    """
    Update only the stock quantity of a product
    
    Args:
        db: Database session
        product_id: ID of product
        quantity: New stock quantity (absolute value, not delta)
    
    Returns:
        Updated Product object if found, None otherwise
    """
    db_product = get_product(db, product_id)
    if not db_product:
        return None
    
    setattr(db_product, "stock_quantity", quantity)
    db.commit()
    db.refresh(db_product)
    
    return db_product