#!/usr/bin/env python
"""Quick script to initialize the database"""
import os
from app import create_app, db
from app.models import User

# Ensure instance directory exists
os.makedirs('instance', exist_ok=True)

# Create app with context
app = create_app()

with app.app_context():
    # Create all tables
    db.create_all()
    print("Database tables created successfully!")

    # Create a default admin user
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            email='admin@example.com',
            role='admin',
            active=True
        )
        admin.set_password('admin123')  # Change this!
        db.session.add(admin)
        db.session.commit()
        print("Default admin user created:")
        print("  Username: admin")
        print("  Password: admin123")
        print("  IMPORTANT: Change this password after first login!")
    else:
        print("Admin user already exists")
