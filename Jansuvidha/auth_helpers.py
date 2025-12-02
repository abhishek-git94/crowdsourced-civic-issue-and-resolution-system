# auth_helpers.py
from functools import wraps
from flask import redirect, url_for, flash
from flask_login import current_user, login_required

def role_required(*roles):
    """
    Decorator to restrict access to users with specific roles.
    Usage:
        @role_required("admin")
        def admin_dashboard(): ...
    """
    def outer(func):
        @wraps(func)
        @login_required
        def wrapper(*args, **kwargs):
            if current_user.role not in roles:
                flash("You do not have permission to view this page.", "danger")
                return redirect(url_for("index"))
            return func(*args, **kwargs)
        return wrapper
    return outer
