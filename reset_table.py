"""
RESET DATABASE TABLES - Drops and recreates all tables

This script completely resets the database by:
1. Dropping all existing tables
2. Recreating them from SQLAlchemy models

USAGE: python reset_tables.py
WARNING: This deletes ALL existing data!

Note: For production with Alembic, use:
  alembic downgrade base
  alembic upgrade head
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from app.database import engine, Base
from app.models.user import User
from app.models.category import Category
from app.models.product import Product
from app.models.order import Order, OrderItem
from app.models.review import Review


def reset_database():
    """
    Complete database reset: drop all tables and recreate them.
    Good for development/testing when you need a clean slate.
    """
    print("=" * 60)
    print("🔄 DATABASE RESET")
    print("=" * 60)
    print()
    
    # Step 1: Drop all tables
    print("📛 Step 1: Dropping all existing tables...")
    Base.metadata.drop_all(bind=engine)
    print("   ✅ All tables dropped.")
    print()
    
    # Step 2: Recreate all tables
    print("🔨 Step 2: Creating tables from models...")
    Base.metadata.create_all(bind=engine)
    print("   ✅ All tables recreated.")
    print()
    
    # Summary
    print("=" * 60)
    print("✅ Database reset complete!")
    print("=" * 60)
    print("\n📋 Tables created:")
    print("   ✅ users")
    print("   ✅ categories")
    print("   ✅ products")
    print("   ✅ orders")
    print("   ✅ order_items")
    print("   ✅ reviews")
    print("\n💡 Next: Run 'python seed_data.py' to add sample data")
    print("💡 Or: 'alembic upgrade head' if using Alembic migrations\n")


if __name__ == "__main__":
    # Safety confirmation
    print("\n⚠️  This will DELETE ALL DATA and recreate tables!")
    confirm = input("Type 'RESET' to proceed: ")
    
    if confirm == "RESET":
        reset_database()
    else:
        print("\n❌ Reset cancelled.")