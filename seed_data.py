"""
SEED DATABASE - Populates database with sample data
Smart version: Checks for existing data before inserting

Creates sample categories, users, products, orders, and reviews
for development and testing purposes.

USAGE: python seed_data.py
NOTE: Run after creating tables with 'alembic upgrade head'

Sample accounts:
  Admin:    admin@example.com / Admin123!
  Customer: customer@example.com / Customer123!
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal
from app.models.user import User
from app.models.category import Category
from app.models.product import Product
from app.models.order import Order, OrderItem, OrderStatus
from app.models.review import Review
from app.utils.hashing import get_password_hash


def seed_database():
    """
    Seed the database with sample data.
    Checks for existing data before inserting to avoid duplicates.
    """
    db = SessionLocal()
    
    try:
        print("=" * 60)
        print("🌱 SEEDING DATABASE WITH SAMPLE DATA")
        print("=" * 60)
        print()
        
        # Check if data already exists
        existing_categories = db.query(Category).count()
        existing_users = db.query(User).count()
        existing_products = db.query(Product).count()
        existing_orders = db.query(Order).count()
        
        if existing_categories > 0 or existing_users > 0:
            print("⚠️  DATABASE ALREADY HAS DATA!")
            print(f"   Categories: {existing_categories}")
            print(f"   Users:      {existing_users}")
            print(f"   Products:   {existing_products}")
            print(f"   Orders:     {existing_orders}")
            print()
            
            response = input("Do you want to CLEAR all data and re-seed? (yes/no): ")
            if response.lower() == "yes":
                print("\n🗑️  Clearing all existing data...")
                # Delete in correct order (respect foreign keys)
                db.query(Review).delete()
                db.query(OrderItem).delete()
                db.query(Order).delete()
                db.query(Product).delete()
                db.query(Category).delete()
                db.query(User).delete()
                db.commit()
                print("   ✅ All data cleared!")
                print()
            else:
                print("\n❌ Seeding cancelled. Database left unchanged.")
                return
        
        # --- 1. CATEGORIES ---
        print("📁 Seeding Categories...")
        categories_data = [
            {"name": "Electronics", "description": "Phones, accessories, and electronic devices"},
            {"name": "Clothing", "description": "Fashion, apparel, and accessories"},
            {"name": "Food & Beverages", "description": "Local and imported food products"},
            {"name": "Home & Garden", "description": "Home improvement and garden supplies"},
        ]
        
        categories = []
        for cat_data in categories_data:
            # Check if category already exists
            existing = db.query(Category).filter(Category.name == cat_data["name"]).first()
            if existing:
                print(f"   ⏭️  '{cat_data['name']}' already exists - skipping")
                categories.append(existing)
            else:
                category = Category(**cat_data)
                db.add(category)
                categories.append(category)
        
        db.commit()
        print(f"   ✅ {len(categories)} categories ready!")
        print()
        
        # --- 2. USERS ---
        print("👤 Seeding Users...")
        
        # Check if admin exists
        admin = db.query(User).filter(User.email == "admin@example.com").first()
        if not admin:
            admin = User(
                email="admin@example.com",
                hashed_password=get_password_hash("Admin123!"),
                full_name="Admin User",
                is_active=True,
                is_admin=True
            )
            db.add(admin)
            print("   ✅ Admin user created")
        else:
            print("   ⏭️  Admin user already exists")
        
        # Check if customer exists
        customer = db.query(User).filter(User.email == "customer@example.com").first()
        if not customer:
            customer = User(
                email="customer@example.com",
                hashed_password=get_password_hash("Customer123!"),
                full_name="Fatmata Kamara",
                is_active=True,
                is_admin=False
            )
            db.add(customer)
            print("   ✅ Customer user created")
        else:
            print("   ⏭️  Customer user already exists")
        
        db.commit()
        print(f"   ✅ Users ready!")
        print(f"      Admin:    admin@example.com / Admin123!")
        print(f"      Customer: customer@example.com / Customer123!")
        print()
        
        # --- 3. PRODUCTS ---
        print("📦 Seeding Products (Sierra Leone market prices in SLE)...")
        
        products_data = [
            # Electronics
            {"name": "Smartphone Charger", "description": "Universal USB-C fast charger", "price": 45.00, "stock_quantity": 100, "category_id": categories[0].id},
            {"name": "Bluetooth Earbuds", "description": "Wireless earbuds with charging case", "price": 150.00, "stock_quantity": 50, "category_id": categories[0].id},
            # Clothing
            {"name": "African Print Shirt", "description": "Traditional Sierra Leone design, cotton", "price": 80.00, "stock_quantity": 30, "category_id": categories[1].id},
            {"name": "Sandals", "description": "Leather sandals, locally made", "price": 120.00, "stock_quantity": 40, "category_id": categories[1].id},
            # Food & Beverages
            {"name": "Palm Oil (1L)", "description": "Pure red palm oil, locally sourced", "price": 35.00, "stock_quantity": 200, "category_id": categories[2].id},
            {"name": "Ground Coffee", "description": "Sierra Leone grown coffee, 500g", "price": 60.00, "stock_quantity": 75, "category_id": categories[2].id},
            # Home & Garden
            {"name": "Garden Hoe", "description": "Heavy-duty farming tool", "price": 90.00, "stock_quantity": 25, "category_id": categories[3].id},
            {"name": "Cooking Pot Set", "description": "3-piece aluminum cooking set", "price": 200.00, "stock_quantity": 15, "category_id": categories[3].id},
        ]
        
        products = []
        products_created = 0
        for prod_data in products_data:
            # Check if product already exists
            existing = db.query(Product).filter(Product.name == prod_data["name"]).first()
            if existing:
                print(f"   ⏭️  '{prod_data['name']}' already exists - skipping")
                products.append(existing)
            else:
                product = Product(**prod_data)
                db.add(product)
                products.append(product)
                products_created += 1
        
        db.commit()
        print(f"   ✅ {products_created} new products created ({len(products)} total across {len(categories)} categories)")
        print()
        
        # --- 4. ORDER (Only if no orders exist) ---
        existing_order_count = db.query(Order).count()
        if existing_order_count == 0:
            print("🛒 Seeding Sample Order...")
            
            order = Order(
                user_id=customer.id,
                status=OrderStatus.PENDING,
                total_amount=0.0,
                shipping_address="12 Siaka Stevens Street, Freetown, Sierra Leone"
            )
            db.add(order)
            db.flush()
            
            # --- 5. ORDER ITEMS ---
            print("📋 Seeding Order Items...")
            
            item1 = OrderItem(
                order_id=order.id,
                product_id=products[0].id,  # Smartphone Charger
                quantity=2,
                unit_price=products[0].price
            )
            db.add(item1)
            
            item2 = OrderItem(
                order_id=order.id,
                product_id=products[2].id,  # African Print Shirt
                quantity=1,
                unit_price=products[2].price
            )
            db.add(item2)
            
            # Update order total
            order.total_amount = (item1.quantity * item1.unit_price) + (item2.quantity * item2.unit_price) # type: ignore
            
            # Deduct stock
            products[0].stock_quantity -= item1.quantity
            products[2].stock_quantity -= item2.quantity
            
            db.commit()
            print(f"   ✅ 1 order with 2 items created!")
            print(f"      Order #{order.id} - Total: SLE {order.total_amount:.2f}")
        else:
            print(f"⏭️  Orders already exist ({existing_order_count} found) - skipping")
            order = db.query(Order).first()  # Get first order for reference
        
        print()
        
        # --- 6. REVIEW (Only if no reviews for this product/user) ---
        existing_review = db.query(Review).filter(
            Review.product_id == products[0].id,
            Review.user_id == customer.id
        ).first()
        
        if not existing_review:
            print("⭐ Seeding Sample Review...")
            
            review = Review(
                product_id=products[0].id,
                user_id=customer.id,
                rating=5,
                comment="Excellent quality charger! Fast charging and durable. Perfect for my small business."
            )
            db.add(review)
            db.commit()
            print(f"   ✅ 1 review created (5 stars) on '{products[0].name}'!")
        else:
            print("⏭️  Review already exists - skipping")
        
        print()
        
        # Final summary
        print("=" * 60)
        print("✅ DATABASE SEEDING COMPLETE!")
        print("=" * 60)
        print("\n📊 Final Database Summary:")
        print(f"   📁 Categories:  {db.query(Category).count()}")
        print(f"   👤 Users:       {db.query(User).count()}")
        print(f"   📦 Products:    {db.query(Product).count()}")
        print(f"   🛒 Orders:      {db.query(Order).count()}")
        print(f"   📋 Order Items: {db.query(OrderItem).count()}")
        print(f"   ⭐ Reviews:     {db.query(Review).count()}")
        print("\n🔑 Test Accounts:")
        print("   Admin:    admin@example.com / Admin123!")
        print("   Customer: customer@example.com / Customer123!")
        print("\n🚀 Ready to start: uvicorn app.main:app --reload\n")
        
    except Exception as e:
        db.rollback()
        print(f"\n❌ Error seeding database: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_database()