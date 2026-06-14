"""
DANGER ZONE - Drops ALL database tables

USE WITH CAUTION - This permanently deletes all tables and data!
Prefer: alembic downgrade base (which tracks rollback history)

USAGE: python drop_tables.py
WARNING: This action cannot be undone!
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


def drop_all_tables():
    """
    Drop all database tables.
    Confirmation required to prevent accidental execution.
    """
    print("=" * 60)
    print("⚠️  WARNING: DROP ALL DATABASE TABLES")
    print("=" * 60)
    print("\nThis will permanently delete ALL tables and data!")
    print("\nTables to be dropped:")
    print("   ❌ order_items")
    print("   ❌ orders")
    print("   ❌ reviews")
    print("   ❌ products")
    print("   ❌ categories")
    print("   ❌ users")
    print()
    
    # Require confirmation to prevent accidents
    confirm = input("Type 'DROP ALL TABLES' to confirm: ")
    
    if confirm == "DROP ALL TABLES":
        print("\n🔨 Dropping all tables...")
        Base.metadata.drop_all(bind=engine)
        print("✅ All tables dropped successfully!")
        print("\n💡 To recreate, run: alembic upgrade head")
    else:
        print("\n❌ Operation cancelled. No tables were dropped.")


if __name__ == "__main__":
    drop_all_tables()