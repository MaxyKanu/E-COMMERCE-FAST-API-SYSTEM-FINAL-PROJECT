"""
List all users in the database
Run: python list_users.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app.database import SessionLocal
from app.models.user import User

db = SessionLocal()

try:
    users = db.query(User).all()
    
    print("=" * 60)
    print("📋 ALL USERS IN DATABASE")
    print("=" * 60)
    
    if not users:
        print("❌ NO USERS FOUND! Database is empty.")
        print("   Run: python seed_data.py")
    else:
        for user in users:
            print(f"\nID:        {user.id}")
            print(f"Email:     {user.email}")
            print(f"Name:      {user.full_name}")
            print(f"Active:    {user.is_active}")
            print(f"Admin:     {user.is_admin}")
            print(f"Created:   {user.created_at}")
            print("-" * 40)
    
    print(f"\nTotal users: {len(users)}")
    
finally:
    db.close()