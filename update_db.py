#!/usr/bin/env python
"""
Ampoulex Database Updater
Creates/updates all database tables with new models
"""

import os
import sys

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from app import create_app, db
try:
    import sqlalchemy
except ImportError:
    sqlalchemy = None
# Ensure werkzeug is installed: pip install werkzeug
try:
    from werkzeug.security import generate_password_hash
except ImportError:
    generate_password_hash = None
from app.models import User, Product, Customer, Inquiry, Order, Employee, Expense, Attendance, Timesheet, LeaveRequest, PayrollPayment


def main():
    print("="*60)
    print("Ampoulex Database Updater")
    print("="*60)
    
    app = create_app()
    
    with app.app_context():
        try:
            # ⚠️ DANGER: This deletes ALL data. Only use in development!
            print("\n⚠️  Dropping all existing tables to ensure clean schema...")
            db.drop_all()
            print("✅ All tables dropped.")
            
            print("\n🏗️  Creating fresh database schema...")
            db.create_all()
            print("✅ Database schema created successfully!")
            
            # Recreate Admin User
            from app.models import User
            if not User.query.filter_by(username='admin').first():
                print("\n👤 Creating default admin user...")
                admin = User(username='admin', email='admin@ampoulex.com', role='admin', is_active=True)
                admin.set_password('admin123')
                db.session.add(admin)
                db.session.commit()
                print("✅ Admin user created (admin/admin123).")
            else:
                print("\n✅ Admin user already exists.")

            # Show Stats
            print("\n" + "="*60)
            print("Database Ready!")
            print("="*60)
            print(f"  - Users: {User.query.count()}")
            print(f"  - Products: {Product.query.count()}")
            print(f"  - Customers: {Customer.query.count()}")
            print(f"  - Orders: {Order.query.count()}")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ ERROR: {e}")
            raise

if __name__ == '__main__':
    main()
if __name__ == '__main__':
    main()