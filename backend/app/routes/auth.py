from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from ..models import User
from .. import oauth

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Handle JSON from Mobile App or Form from Web
        if request.is_json:
            data = request.get_json()
            name = data.get("name")
            email = data.get("email", "").strip().lower()
            password = data.get("password")
        else:
            name = request.form.get("name")
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password")

        if not name or not email or not password:
            if request.is_json:
                return {"success": False, "message": "All fields are required."}, 400
            flash("All fields are required.", "warning")
            return redirect(url_for("auth.register"))

        existing = User.objects(email=email).first()
        if existing:
            if request.is_json:
                return {"success": False, "message": "Email already registered."}, 400
            flash("Email already registered.", "danger")
            return redirect(url_for("auth.register"))

        new_user = User(
            name=name,
            email=email,
            password=generate_password_hash(password),
            role="citizen"
        )
        new_user.save()

        if request.is_json:
            return {"success": True, "message": "Registration successful!"}

        flash("Registration successful! Please login.", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Handle JSON from Mobile App or Form from Web
        if request.is_json:
            data = request.get_json()
            email = data.get("email", "").strip().lower()
            password = data.get("password")
        else:
            email = request.form.get("email", "").strip().lower()
            password = request.form.get("password")

        user = User.objects(email=email).first()

        if not user or not check_password_hash(user.password, password):
            if request.is_json:
                return {"success": False, "message": "Invalid email or password."}, 401
            flash("Invalid email or password.", "danger")
            return redirect(url_for("auth.login"))

        login_user(user)
        session["user_id"] = str(user.id)
        session["user_name"] = user.name
        session["user_role"] = user.role

        if request.is_json:
            return {
                "success": True,
                "user": {
                    "id": str(user.id),
                    "name": user.name,
                    "email": user.email,
                    "role": user.role
                }
            }

        flash("Login successful!", "success")
        next_page = request.args.get("next")
        return redirect(next_page or url_for("main.index"))

    return render_template("auth/login.html")

@auth_bp.route('/login/google')
def login_google():
    redirect_uri = url_for('auth.authorize', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@auth_bp.route('/authorize')
def authorize():
    try:
        token = oauth.google.authorize_access_token()
        resp = oauth.google.get('https://openidconnect.googleapis.com/v1/userinfo')
        user_info = resp.json()
        
        email = user_info.get('email')
        name = user_info.get('name')
        
        user = User.objects(email=email).first()
        if not user:
            # Auto-register new SSO user with a random password since they use Google
            import secrets
            random_password = secrets.token_urlsafe(16)
            user = User(
                name=name,
                email=email,
                password=generate_password_hash(random_password),
                role="citizen"
            )
            user.save()
            
        login_user(user)
        session["user_id"] = str(user.id)
        session["user_name"] = user.name
        session["user_role"] = user.role
        
        flash("Logged in with Google!", "success")
        return redirect(url_for('main.index'))
    except Exception as e:
        flash(f"SSO Login Failed: {str(e)}", "danger")
        return redirect(url_for('auth.login'))

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for("auth.login"))

@auth_bp.route("/profile")
@login_required
def profile():
    return render_template("auth/profile.html", user=current_user)

@auth_bp.route("/firebase-login", methods=["POST"])
def firebase_login():
    from firebase_admin import auth as firebase_auth
    import firebase_admin
    import jwt
    import logging

    try:
        data = request.get_json()
        id_token = data.get("idToken")
        payload_name = data.get("name")
        
        if not id_token:
            return {"success": False, "error": "No token provided"}, 400
            
        if firebase_admin._apps:
            decoded_token = firebase_auth.verify_id_token(id_token)
        else:
            # DEV MODE FALLBACK
            logging.warning("DEV MODE: Decoding Firebase token WITHOUT signature verification.")
            decoded_token = jwt.decode(id_token, options={"verify_signature": False})
            
        email = decoded_token.get("email")
        name = payload_name or decoded_token.get("name", email.split('@')[0])
        
        user = User.objects(email=email).first()
        if not user:
            # Register user
            import secrets
            random_password = secrets.token_urlsafe(16)
            user = User(
                name=name,
                email=email,
                password=generate_password_hash(random_password),
                role="citizen"
            )
            user.save()
            
        login_user(user)
        session["user_id"] = str(user.id)
        session["user_name"] = user.name
        session["user_role"] = user.role
        
        return {"success": True, "message": "Logged in successfully"}
        
    except Exception as e:
        import logging
        logging.error(f"Firebase auth error: {e}")
        return {"success": False, "error": str(e)}, 401
