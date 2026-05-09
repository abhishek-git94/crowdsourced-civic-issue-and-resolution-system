from app import create_app
from app.models import User
from werkzeug.security import generate_password_hash
import os

app = create_app()

def create_admin():
    with app.app_context():
        email = "admin@js.com"
        password = "admin123"
        name = "System Admin"
        
        existing = User.objects(email=email).first()
        if existing:
            print(f"User {email} already exists. Updating role to admin.")
            existing.role = "admin"
            existing.password = generate_password_hash(password)
            existing.save()
        else:
            admin = User(
                name=name,
                email=email,
                password=generate_password_hash(password),
                role="admin"
            )
            admin.save()
            print(f"Admin user created successfully!")
            print(f"Email: {email}")
            print(f"Password: {password}")

if __name__ == "__main__":
    create_admin()
