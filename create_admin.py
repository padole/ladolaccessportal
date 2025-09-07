#!/usr/bin/env python3
"""
Script to create an admin user with username 'adole_peter@ladol.com' and password 'Wealth4110@@'
"""

from myapp import create_app
from myapp.models import db, Admin
from werkzeug.security import generate_password_hash

def create_admin_user():
    app = create_app()
    with app.app_context():
        # Check if admin user already exists
        existing_admin = Admin.query.filter_by(admin_username='adole_peter@ladol.com').first()
        if existing_admin:
            print("Admin user 'adole_peter@ladol.com' already exists. Skipping creation.")
            return

        # Create new admin user
        hashed_password = generate_password_hash('Wealth4110@@')
        admin_user = Admin()
        admin_user.admin_username = 'adole_peter@ladol.com'
        admin_user.admin_password = hashed_password

        db.session.add(admin_user)
        db.session.commit()
        print("Admin user 'adole_peter@ladol.com' created successfully with password 'Wealth4110@@'")

if __name__ == '__main__':
    create_admin_user()
