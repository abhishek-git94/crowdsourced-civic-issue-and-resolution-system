from app import create_app
from app.models import User
import os

app = create_app()
with app.app_context():
    users = User.objects()
    if not users:
        print("No users found in database.")
    else:
        print("Users and Roles:")
        for u in users:
            print(f"Email: {u.email} | Role: {u.role}")
