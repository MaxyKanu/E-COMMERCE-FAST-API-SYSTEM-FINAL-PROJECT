"""
BACKUP METHOD ONLY - Creates all database tables

PRIMARY method is: alembic upgrade head
This file kept as backup/learning reference.

SQLAlchemy reads Python models and converts them to 
PostgreSQL CREATE TABLE statements automatically.

USAGE: python create_tables.py
WARNING: This doesn't track migrations like Alembic does.
         For production, always use Alembic.
"""

import sys
import os

# Add the parent directory to path so we can import app
sys.path.insert(0, os.path.dirname(__file__))

from app.database import engine, Base
from app.models.user import User
from app.models.category import Category
from app.models.product import Product
from app.models.order import Order, OrderItem
from app.models.review import Review


def create_all_tables():
    """
    Create all tables defined in SQLAlchemy models.
    Tables only created if they don't already exist.
    """
    print("=" * 50)
    print("CREATING DATABASE TABLES (Backup Method)")
    print("=" * 50)
    print("\n📋 Models found:")
    print(f"   ✅ User")
    print(f"   ✅ Category")
    print(f"   ✅ Product")
    print(f"   ✅ Order")
    print(f"   ✅ OrderItem")
    print(f"   ✅ Review")
    print("\n🔨 Creating tables...")
    
    # SQLAlchemy reads all models and generates CREATE TABLE SQL
    Base.metadata.create_all(bind=engine)
    
    print("\n✅ All tables created successfully!")
    print("\n⚠️  REMINDER: Primary method is 'alembic upgrade head'")
    print("   This script is kept only as backup reference.\n")


if __name__ == "__main__":
    create_all_tables()