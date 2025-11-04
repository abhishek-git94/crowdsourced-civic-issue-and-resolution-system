# routes/issues.py
from flask import Blueprint, jsonify, request
from database import SessionLocal
from models import Issue

issue_bp = Blueprint("issues", __name__)

@issue_bp.post("/issues")
def create_issue():
    data = request.get_json(force=True)
    with SessionLocal() as db:
        issue = Issue(
            reporter_id=data["reporter_id"],
            title=data["title"],
            description=data.get("description"),
            category=data.get("category"),
        )
        db.add(issue)
        db.commit()
        db.refresh(issue)
        return jsonify({"id": issue.id, "title": issue.title}), 201

@issue_bp.get("/issues")
def list_issues():
    with SessionLocal() as db:
        issues = db.query(Issue).all()
        return jsonify([
            {
                "id": i.id,
                "title": i.title,
                "status": i.status,
                "category": i.category,
                "created_at": i.created_at,
                "reporter_id": i.reporter_id
            } for i in issues
        ])
