from mongoengine import connect
from werkzeug.security import generate_password_hash

def init_db(app):
    db_uri = app.config.get('MONGODB_SETTINGS', {}).get('host')
    connect(host=db_uri)
    
    # Ensure default admin exists
    ensure_admin_exists()

def ensure_admin_exists():
    from .models import User
    email = "admin@js.com"
    if not User.objects(email=email).first():
        admin = User(
            name="System Admin",
            email=email,
            password=generate_password_hash("admin123"),
            role="admin"
        )
        admin.save()
        print(f"Default admin created: {email}")
