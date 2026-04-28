from flask import Blueprint, render_template
from flask_login import login_required
from ..models import Issue

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def index():
    return render_template("index.html")

@main_bp.route("/map")
@login_required
def issue_map():
    try:
        issues = Issue.objects.all()
    except Exception:
        issues = []

    issue_list = []
    for i in issues:
        issue_list.append({
            "id": str(i.id),
            "title": (i.issue[:40] + "...") if i.issue else "No description",
            "location": i.location,
            "lat": None,
            "lng": None,
            "status": i.status,
            "category": i.category,
            "upvotes": i.upvotes
        })
    return render_template("map.html", issues=issue_list)
