"""
DATABASE VERIFICATION - Tests connection and counts records

Verifies database connectivity and provides a summary of
all records in each table.

USAGE: python verify_database.py
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal, engine
from app.models.user import User
from app.models.category import Category
from app.models.product import Product
from app.models.order import Order, OrderItem
from app.models.review import Review
from sqlalchemy import text


def verify_database():
    """
    Verify database connection and count records in all tables.
    Prints a summary report of the database state.
    """
    print("=" * 50)
    print("🔍 DATABASE VERIFICATION")
    print("=" * 50)
    print()
    
    # Test database connection
    print("🔌 Testing database connection...")
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("   ✅ Database connection successful!")
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        return
    
    print()
    print("📊 Counting records...")
    print()
    
    # Create session and count records
    db = SessionLocal()
    
    try:
        # Count records in each table
        user_count = db.query(User).count()
        category_count = db.query(Category).count()
        product_count = db.query(Product).count()
        order_count = db.query(Order).count()
        order_item_count = db.query(OrderItem).count()
        review_count = db.query(Review).count()
        
        # Print verification report
        print("=" * 50)
        print("DATABASE VERIFICATION REPORT")
        print("=" * 50)
        print(f"✅ Users:       {user_count} records")
        print(f"✅ Categories:  {category_count} records")
        print(f"✅ Products:    {product_count} records")
        print(f"✅ Orders:      {order_count} records")
        print(f"✅ Order Items: {order_item_count} records")
        print(f"✅ Reviews:     {review_count} records")
        print("=" * 50)
        
        total_records = user_count + category_count + product_count + order_count + order_item_count + review_count
        
        if total_records > 0:
            print(f"📈 Total records across all tables: {total_records}")
            print()
            print("🎯 Database verification complete!")
            print("✅ Database is ready for use!")
        else:
            print()
            print("⚠️  Database is empty. Run seed_data.py to add sample data:")
            print("   python seed_data.py")
        
    except Exception as e:
        print(f"\n❌ Verification failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    verify_database()