# auth_blueprint.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user

from database import SessionLocal
from models import User

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


# ---------------------------------------------------
# REGISTER
# ---------------------------------------------------
@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")

        if not name or not email or not password:
            flash("All fields are required.", "warning")
            return redirect(url_for("auth.register"))

        with SessionLocal() as db:
            # Check if email exists
            existing = db.query(User).filter_by(email=email).first()
            if existing:
                flash("Email already registered.", "danger")
                return redirect(url_for("auth.register"))

            new_user = User(
                name=name,
                email=email,
                password=generate_password_hash(password),
                role="citizen"
            )
            db.add(new_user)
            db.commit()

        flash("Registration successful! Please login.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")


# ---------------------------------------------------
# LOGIN
# ---------------------------------------------------
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        with SessionLocal() as db:
            user = db.query(User).filter_by(email=email).first()

        if not user or not check_password_hash(user.password, password):
            flash("Invalid email or password.", "danger")
            return redirect(url_for("auth.login"))

        # Flask-Login login
        login_user(user)

        # Store extra info in session (used by navbar)
        session["user_id"] = user.id
        session["user_name"] = user.name
        session["user_role"] = user.role

        flash("Login successful!", "success")

        next_page = request.args.get("next")
        return redirect(next_page or url_for("index"))

    return render_template("auth/login.html")


# ---------------------------------------------------
# LOGOUT
# ---------------------------------------------------
@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    session.clear()

    flash("Logged out successfully.", "info")
    return redirect(url_for("auth.login"))


# ---------------------------------------------------
# PROFILE PAGE
# ---------------------------------------------------
@auth_bp.route("/profile")
@login_required
def profile():
    return render_template("auth/profile.html", user=current_user)
