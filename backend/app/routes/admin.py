from io import BytesIO
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, make_response, current_app
from flask_login import login_required, current_user
from ..models import Issue, User
from ..utils.helpers import role_required

try:
    from xhtml2pdf import pisa
    PDF_AVAILABLE = True
except Exception:
    pisa = None
    PDF_AVAILABLE = False

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")

@admin_bp.route("/dashboard")
@role_required("admin")
def dashboard():
    try:
        total_issues = Issue.objects.count()
        pending_count = Issue.objects(status="Pending").count()
        resolved_count = Issue.objects(status="Resolved").count()
        linked_count = Issue.objects(status="Linked").count()
        critical_count = Issue.objects(severity="High").count()

        # Status distribution
        status_pipeline = [{"$group": {"_id": "$status", "count": {"$sum": 1}}}]
        status_rows = list(Issue.objects.aggregate(status_pipeline))
        status_labels = [row["_id"] or "Unknown" for row in status_rows]
        status_values = [row["count"] for row in status_rows]

        # Category distribution
        category_pipeline = [{"$group": {"_id": "$category", "count": {"$sum": 1}}}]
        category_rows = list(Issue.objects.aggregate(category_pipeline))
        category_labels = [row["_id"] or "Uncategorized" for row in category_rows]
        category_values = [row["count"] for row in category_rows]

        # Daily trends (last 14 days)
        daily_pipeline = [
            {"$group": {
                "_id": {"$dateToString": {"format": "%Y-%m-%d", "date": "$created_at"}},
                "count": {"$sum": 1}
            }},
            {"$sort": {"_id": 1}},
            {"$limit": 14}
        ]
        daily_rows = list(Issue.objects.aggregate(daily_pipeline))
        daily_labels = [datetime.strptime(row["_id"], "%Y-%m-%d").strftime("%d-%b") for row in daily_rows]
        daily_values = [row["count"] for row in daily_rows]

        # Prioritized issues
        prioritized_issues = Issue.objects(status__ne="Resolved").order_by('-upvotes').limit(10)
        
        # Department Rankings (Efficiency Engine)
        rankings_pipeline = [
            {"$match": {"status": {"$in": ["Resolved", "Resolved (Unconfirmed)"]}, "assigned_to": {"$ne": None}, "resolved_at": {"$ne": None}}},
            {"$project": {
                "department": "$assigned_to",
                "resolution_time": {
                    "$divide": [{"$subtract": ["$resolved_at", "$created_at"]}, 3600000] # hours
                }
            }},
            {"$group": {
                "_id": "$department",
                "avg_hours": {"$avg": "$resolution_time"},
                "resolved_count": {"$sum": 1}
            }},
            {"$sort": {"avg_hours": 1}}
        ]
        department_rankings = list(Issue.objects.aggregate(rankings_pipeline))
        
    except Exception as e:
        current_app.logger.error(f"Dashboard error: {e}")
        flash("Database error loading dashboard.", "danger")
        return redirect(url_for("main.index"))

    return render_template(
        "admin/dashboard.html",
        total_issues=total_issues, pending_count=pending_count,
        resolved_count=resolved_count, linked_count=linked_count,
        critical_count=critical_count, status_labels=status_labels,
        status_values=status_values, category_labels=category_labels,
        category_values=category_values, daily_labels=daily_labels,
        daily_values=daily_values, prioritized_issues=prioritized_issues,
        department_rankings=department_rankings
    )

@admin_bp.route("/issues")
@role_required("admin")
def issues():
    status = request.args.get("status", "all")
    try:
        q = Issue.objects.order_by('-created_at')
        if status != "all":
            q = q.filter(status=status)
        issues = q.all()
        workers = User.objects(role="worker")
    except Exception:
        flash("Database error.", "danger")
        return redirect(url_for("admin.dashboard"))

    return render_template("admin/issues.html", issues=issues, workers=workers, selected_status=status)

@admin_bp.route("/issues/<issue_id>/assign", methods=["POST"])
@role_required("admin")
def assign_issue(issue_id):
    assigned_to = request.form.get("assigned_to")
    status = request.form.get("status_filter", "all")
    try:
        issue = Issue.objects(id=issue_id).first()
        if not issue:
            flash("Issue not found.", "danger")
            return redirect(url_for("admin.issues", status=status))
        issue.assigned_to = assigned_to if assigned_to != "none" else None
        issue.save()
    except Exception:
        flash("Database error assigning issue.", "danger")
        return redirect(url_for("admin.issues", status=status))

    flash("Issue assigned successfully.", "success")
    return redirect(url_for("admin.issues", status=status))

from ..utils.notifications import notify_status_change

@admin_bp.route("/issues/<issue_id>/status", methods=["POST"])
@role_required("admin")
def update_status(issue_id):
    new_status = request.form.get("status")
    status_filter = request.form.get("status_filter", "all")
    try:
        issue = Issue.objects(id=issue_id).first()
        if not issue:
            flash("Issue not found.", "danger")
            return redirect(url_for("admin.issues", status=status_filter))
        
        # Map "Resolved" to "Resolved (Unconfirmed)" to satisfy "No Fake Resolves"
        if new_status == "Resolved":
            new_status = "Resolved (Unconfirmed)"
            
        issue.status = new_status
        issue.save()
        
        # Trigger push notification
        notify_status_change(issue)
        
    except Exception:
        flash("Database error updating status.", "danger")
        return redirect(url_for("admin.issues", status=status_filter))

    flash(f"Status updated to {new_status}.", "success")
    return redirect(url_for("admin.issues", status=status_filter))

@admin_bp.route("/issues/<issue_id>/pdf")
@role_required("admin")
def issue_pdf(issue_id):
    try:
        issue = Issue.objects(id=issue_id).first()
        if not issue:
            flash("Issue not found.", "danger")
            return redirect(url_for("admin.issues"))
    except Exception:
        flash("Database error.", "danger")
        return redirect(url_for("admin.issues"))

    html = render_template("admin/issue_pdf.html", issue=issue)
    if not PDF_AVAILABLE:
        return html, 200, {"Content-Type": "text/html; charset=utf-8"}

    result = BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=result)
    if pisa_status.err:
        flash("Failed to generate PDF.", "danger")
        return redirect(url_for("admin.issues"))

    pdf = result.getvalue()
    resp = make_response(pdf)
    resp.headers["Content-Type"] = "application/pdf"
    resp.headers["Content-Disposition"] = f"attachment; filename=issue_{issue.id}.pdf"
    return resp

@admin_bp.route("/manager/dashboard")
@role_required("manager")
def manager_dashboard():
    try:
        # We assume assigned_to matches the user's name or email
        assigned = Issue.objects(assigned_to__in=[current_user.name, current_user.email])
    except Exception:
        flash("Database error.", "danger")
        assigned = []
    
    return render_template("manager_dashboard.html", assigned=assigned)

@admin_bp.route("/manager/update/<issue_id>", methods=["POST"])
@role_required("manager")
def manager_update(issue_id):
    new_status = request.form.get("status")
    try:
        issue = Issue.objects(id=issue_id).first()
        if not issue:
            flash("Issue not found.", "danger")
            return redirect(url_for("admin.manager_dashboard"))
        
        # satisfy "No Fake Resolves" - map to unconfirmed
        if new_status == "Resolved":
            new_status = "Resolved (Unconfirmed)"
            
        issue.status = new_status
        issue.save()
        
        # Trigger push notification
        notify_status_change(issue)
        
    except Exception:
        flash("Update failed.", "danger")
    
    flash("Status updated.", "success")
    return redirect(url_for("admin.manager_dashboard"))
