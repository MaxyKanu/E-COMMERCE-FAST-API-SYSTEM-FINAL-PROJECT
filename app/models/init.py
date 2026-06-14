"""
SQLAlchemy Models Package
Import all models here for easy access throughout the application
"""

from app.models.user import User
from app.models.category import Category
from app.models.product import Product
from app.models.order import Order, OrderItem
from app.models.review import Review

# This allows importing models like:
# from app.models import User, Product, Order, etc.