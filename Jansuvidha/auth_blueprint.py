# auth_blueprint.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash

from database import SessionLocal
from models import User, Issue

auth_bp = Blueprint("auth", __name__, template_folder="templates", static_folder="static")

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        role = request.form.get("role", "citizen")  # only admins should set roles in UI; default citizen

        if not name or not email or not password:
            flash("Please fill all required fields.", "danger")
            return redirect(url_for("auth.register"))

        hashed = generate_password_hash(password)
        with SessionLocal() as db:
            existing = db.query(User).filter_by(email=email).first()
            if existing:
                flash("Email already registered.", "warning")
                return redirect(url_for("auth.register"))
            user = User(name=name, email=email, password=hashed, role=role)
            db.add(user)
            db.commit()
            flash("Registration successful. Please login.", "success")
            return redirect(url_for("auth.login"))
    return render_template("auth/register.html")


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        with SessionLocal() as db:
            user = db.query(User).filter_by(email=email).first()
            if not user or not check_password_hash(user.password, password):
                flash("Invalid email or password.", "danger")
                return redirect(url_for("auth.login"))

            session["user_id"] = user.id
            session["user_name"] = user.name
            session["user_role"] = user.role
            flash("Login successful.", "success")
            next_page = request.args.get("next") or url_for("index")
            return redirect(next_page)
    return render_template("auth/login.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("Logged out.", "info")
    return redirect(url_for("index"))


@auth_bp.route("/profile")
def profile():
    uid = session.get("user_id")
    if not uid:
        flash("Please login to view profile.", "warning")
        return redirect(url_for("auth.login"))

    with SessionLocal() as db:
        user = db.query(User).filter_by(id=uid).first()
        issues = db.query(Issue).filter_by(name=user.name).order_by(Issue.created_at.desc()).all()
    return render_template("auth/profile.html", user=user, issues=issues)
