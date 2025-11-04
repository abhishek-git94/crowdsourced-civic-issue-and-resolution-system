# routes/users.py
from flask import Blueprint, jsonify, request
from database import SessionLocal
from models import User

user_bp = Blueprint("users", __name__)

@user_bp.post("/users")
def create_user():
    data = request.get_json(force=True)
    with SessionLocal() as db:
        user = User(email=data["email"], name=data.get("name"))
        db.add(user)
        db.commit()
        db.refresh(user)
        return jsonify({"id": user.id, "email": user.email}), 201

@user_bp.get("/users")
def list_users():
    with SessionLocal() as db:
        users = db.query(User).all()
        return jsonify([
            {"id": u.id, "email": u.email, "name": u.name}
            for u in users
        ])
