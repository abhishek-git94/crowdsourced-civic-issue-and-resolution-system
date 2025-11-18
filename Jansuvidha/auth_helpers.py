from functools import wraps
from flask import session, redirect, url_for, flash, request

def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            flash("Please login to access this page.", "warning")
            return redirect(url_for("auth.login", next=request.path))
        return func(*args, **kwargs)
    return wrapper


def role_required(*roles):
    def outer(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user_role = session.get("user_role")
            if not user_role:
                flash("Please login first.", "warning")
                return redirect(url_for("auth.login", next=request.path))

            if user_role not in roles:
                flash("You do not have permission to view this page.", "danger")
                return redirect(url_for("index"))
            return func(*args, **kwargs)
        return wrapper
    return outer