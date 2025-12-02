# app.py — full application (cleaned + robust)
from dotenv import load_dotenv
load_dotenv()

import os
import json
from datetime import datetime
from io import BytesIO

from flask import (
    Flask, request, render_template, redirect,
    url_for, flash, jsonify, session, make_response
)
from werkzeug.utils import secure_filename

from sqlalchemy import func
from sqlalchemy.exc import OperationalError

# optional PDF lib
try:
    from xhtml2pdf import pisa  # pip install xhtml2pdf
    PDF_AVAILABLE = True
except Exception:
    pisa = None
    PDF_AVAILABLE = False

# ------------------------------------------
# Create Flask App (single instance)
# ------------------------------------------
app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = os.getenv("SECRET_KEY", "secret123")

# ------------------------------------------
# Flask-Login Setup
# ------------------------------------------
from flask_login import LoginManager, login_required, current_user
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"
login_manager.login_message_category = "warning"

# ------------------------------------------
# Database + Models Import (AFTER app init)
# ------------------------------------------
from database import engine, SessionLocal
from models import Base, User, Issue, Upvote

@login_manager.user_loader
def load_user(user_id):
    try:
        with SessionLocal() as db:
            return db.get(User, int(user_id))
    except Exception:
        return None

# ------------------------------------------
# Other Imports That Use app/models
# ------------------------------------------
from ai_analyzer import CivicAIAnalyzer
from utils.duplicate_detector import (
    get_local_embedding, get_openai_embedding,
    cosine_similarity, embed_to_json
)
from auth_blueprint import auth_bp
from auth_helpers import role_required

# ------------------------------------------
# Register Blueprint
# ------------------------------------------
app.register_blueprint(auth_bp)

# ------------------------------------------
# Ensure Upload Directory Exists
# ------------------------------------------
os.makedirs(os.path.join(app.static_folder, "uploads"), exist_ok=True)

# ------------------------------------------
# Duplicate Detection Settings
# ------------------------------------------
EMBED_BACKEND = os.getenv("EMBED_BACKEND", "local")
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", 0.78))
RECENT_CHECK_COUNT = int(os.getenv("RECENT_CHECK_COUNT", 50))

# ------------------------------------------
# AI Analyzer
# ------------------------------------------
ai_analyzer = CivicAIAnalyzer(
    text_model=os.getenv("OLLAMA_MODEL", "llama3"),
    yolo_model=os.getenv("YOLO_MODEL", "yolov8_civic.pt")
)

print("SQLAlchemy engine ready to go!")

# ======================================================================
# ROUTES
# ======================================================================

@app.route("/")
def index():
    return render_template("index.html")


# ------------------------------------------------------
# View Issues (with has_upvoted flag)
# ------------------------------------------------------
@app.route("/view")
@login_required
def view_issues():
    try:
        with SessionLocal() as db:
            issues = db.query(Issue).order_by(Issue.created_at.desc()).all()

            # Issues user upvoted (returns list of single-column rows)
            rows = db.query(Upvote.issue_id).filter_by(user_id=current_user.id).all()
            voted_ids = {r[0] for r in rows}

            # Add flag for template
            for issue in issues:
                issue.has_upvoted = issue.id in voted_ids

        return render_template("view_issues.html", issues=issues)
    except OperationalError:
        app.logger.exception("DB error in view_issues")
        flash("Cannot access the database right now. Try again later.", "danger")
        return render_template("downtime.html")


# ------------------------------------------------------
# AJAX Upvote / Devote Toggle
# ------------------------------------------------------
@app.route("/issue/<int:issue_id>/upvote", methods=["POST"])
@login_required
def upvote_issue(issue_id):

    is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"

    try:
        with SessionLocal() as db:
            issue = db.query(Issue).filter_by(id=issue_id).first()
            if not issue:
                if is_ajax:
                    return jsonify({"success": False, "error": "Issue not found"}), 404
                flash("Issue not found.", "danger")
                return redirect(url_for("view_issues"))

            user_id = current_user.id

            existing_vote = db.query(Upvote).filter_by(
                user_id=user_id, issue_id=issue_id
            ).first()

            # Toggle remove vote
            if existing_vote:
                db.delete(existing_vote)
                issue.upvotes = max(0, issue.upvotes - 1)
                db.commit()

                if is_ajax:
                    return jsonify({
                        "success": True,
                        "upvoted": False,
                        "upvotes": issue.upvotes,
                        "status": "removed"
                    })

                flash("Vote removed.", "info")
                return redirect(url_for("view_issues"))

            # Add vote
            new_vote = Upvote(user_id=user_id, issue_id=issue_id)
            db.add(new_vote)
            issue.upvotes += 1
            db.commit()

            if is_ajax:
                return jsonify({
                    "success": True,
                    "upvoted": True,
                    "upvotes": issue.upvotes,
                    "status": "added"
                })

            flash("Upvoted!", "success")
            return redirect(url_for("view_issues"))
    except OperationalError:
        app.logger.exception("DB error in upvote")
        if is_ajax:
            return jsonify({"success": False, "error": "Database error"}), 500
        flash("Database error. Please try again later.", "danger")
        return redirect(url_for("view_issues"))


# ------------------------------------------------------
# List Users Who Upvoted
# ------------------------------------------------------
@app.route("/issue/<int:issue_id>/upvote/list")
@login_required
def upvote_list(issue_id):

    try:
        with SessionLocal() as db:
            rows = (
                db.query(Upvote, User)
                .join(User, Upvote.user_id == User.id)
                .filter(Upvote.issue_id == issue_id)
                .all()
            )

            usernames = [user.name for (up, user) in rows]
    except OperationalError:
        app.logger.exception("DB error in upvote_list")
        return jsonify({"users": []})

    return jsonify({"users": usernames})


# ------------------------------------------------------
# REPORT ISSUE
# ------------------------------------------------------
@app.route("/report", methods=["GET", "POST"])
@login_required
def report_issue():
    if request.method == "POST":

        name = current_user.name
        location = request.form.get("location", "")
        file = request.files.get("attachment")

        analysis = None
        file_path = None

        # Handle Image Upload
        if file and file.filename:
            uploads = os.path.join(app.static_folder, "uploads")
            filename = secure_filename(file.filename)
            full_path = os.path.join(uploads, filename)
            file.save(full_path)
            file_path = f"uploads/{filename}"

            try:
                analysis = ai_analyzer.analyze_civic_issue(full_path, location)
                issue_text = analysis.get("description", "")
            except Exception:
                app.logger.exception("AI analyze error")
                issue_text = request.form.get("issue", "")
        else:
            issue_text = request.form.get("issue", "")

        # Prepare embedding text
        embed_text = f"{issue_text}\nLocation: {location}"
        if analysis and analysis.get("detected_objects"):
            embed_text += "\nObjects: " + ", ".join(analysis["detected_objects"])

        try:
            embedding = (
                get_openai_embedding(embed_text)
                if EMBED_BACKEND == "openai"
                else get_local_embedding(embed_text)
            )
        except Exception:
            embedding = None

        # Duplicate Detection (simple recent-scan)
        similar = []
        if embedding:
            try:
                with SessionLocal() as db:
                    recent = (
                        db.query(Issue)
                        .filter(Issue.embedding != None)
                        .order_by(Issue.created_at.desc())
                        .limit(RECENT_CHECK_COUNT)
                        .all()
                    )
            except OperationalError:
                recent = []

            for old in recent:
                try:
                    old_emb = json.loads(old.embedding)
                    sim = cosine_similarity(embedding, old_emb)
                    if sim >= SIMILARITY_THRESHOLD:
                        similar.append({
                            "id": old.id,
                            "issue": old.issue,
                            "location": old.location,
                            "upvotes": old.upvotes,
                            "similarity": round(sim, 3)
                        })
                except Exception:
                    continue

        # If duplicate detected -> ask user to link or force create
        if similar:
            session["_pending_issue"] = {
                "name": name,
                "issue": issue_text,
                "location": location,
                "file_path": file_path,
                "analysis": analysis,
                "embedding": embed_to_json(embedding) if embedding else None
            }
            return render_template(
                "confirm_duplicate.html",
                candidates=similar,
                pending=session["_pending_issue"]
            )

        # Normal Save
        try:
            with SessionLocal() as db:
                new_issue = Issue(
                    name=name,
                    issue=issue_text,
                    location=location,
                    file=file_path,
                    status="Pending",
                    category=analysis.get("category") if analysis else None,
                    confidence=analysis.get("confidence") if analysis else None,
                    severity=analysis.get("severity") if analysis else None,
                    embedding=embed_to_json(embedding) if embedding else None,
                    user_id=current_user.id
                )
                db.add(new_issue)
                db.commit()
        except OperationalError:
            app.logger.exception("DB error while saving new issue")
            flash("Database error. Could not save your report.", "danger")
            return redirect(url_for("report_issue"))

        flash("Issue reported successfully!", "success")
        return redirect(url_for("report_issue"))

    return render_template("report_issues.html")


# ------------------------------------------------------
# Confirm Duplicate Link
# ------------------------------------------------------
@app.route("/report/confirm_link", methods=["POST"])
@login_required
def confirm_link():
    pending = session.pop("_pending_issue", None)
    link_to = int(request.form.get("link_to", 0))

    if not pending:
        flash("No pending issue!", "danger")
        return redirect(url_for("report_issue"))

    try:
        with SessionLocal() as db:
            new_issue = Issue(
                name=pending["name"],
                issue=pending["issue"],
                location=pending["location"],
                file=pending["file_path"],
                status="Linked",
                is_duplicate_of=link_to,
                embedding=pending.get("embedding"),
                user_id=current_user.id
            )
            db.add(new_issue)
            db.commit()
    except OperationalError:
        app.logger.exception("DB error in confirm_link")
        flash("Database error. Could not link issue.", "danger")
        return redirect(url_for("report_issue"))

    flash("Issue linked successfully.", "success")
    return redirect(url_for("view_issues"))


# ------------------------------------------------------
# Force Create
# ------------------------------------------------------
@app.route("/report/force_create", methods=["POST"])
@login_required
def force_create():
    pending = session.pop("_pending_issue", None)

    if not pending:
        flash("Nothing to create.", "danger")
        return redirect(url_for("report_issue"))

    try:
        with SessionLocal() as db:
            new_issue = Issue(
                name=pending["name"],
                issue=pending["issue"],
                location=pending["location"],
                file=pending["file_path"],
                status="Pending",
                embedding=pending.get("embedding"),
                user_id=current_user.id
            )
            db.add(new_issue)
            db.commit()
    except OperationalError:
        app.logger.exception("DB error in force_create")
        flash("Database error. Could not create issue.", "danger")
        return redirect(url_for("report_issue"))

    flash("Issue created.", "success")
    return redirect(url_for("view_issues"))


# ------------------------------------------------------
# AI API
# ------------------------------------------------------
@app.route("/analyze-image", methods=["POST"])
def analyze_image_api():
    try:
        file = request.files.get("image")
        location = request.form.get("location", "Unknown")

        if not file:
            return jsonify({"error": "No image provided"}), 400

        uploads = os.path.join(app.static_folder, "uploads")
        filename = f"tmp_{datetime.now().timestamp()}_{secure_filename(file.filename)}"
        path = os.path.join(uploads, filename)
        file.save(path)

        result = ai_analyzer.analyze_civic_issue(path, location)

        return jsonify(result)
    except Exception as e:
        app.logger.exception("analyze-image error")
        return jsonify({"error": str(e)}), 500


# ------------------------------------------------------
# Trending
# ------------------------------------------------------
@app.route("/trending")
@login_required
def trending_issues():
    try:
        with SessionLocal() as db:
            issues = (
                db.query(Issue)
                .order_by(Issue.upvotes.desc())
                .limit(5)
                .all()
            )
    except OperationalError:
        issues = []
    return render_template("trending_issues.html", issues=issues)


# ------------------------------------------------------
# Admin dashboard & analytics
# ------------------------------------------------------
@app.route("/admin/dashboard")
@role_required("admin")
def admin_dashboard():
    try:
        with SessionLocal() as db:
            total_issues = db.query(Issue).count()
            pending_count = db.query(Issue).filter(Issue.status == "Pending").count()
            resolved_count = db.query(Issue).filter(Issue.status == "Resolved").count()
            linked_count = db.query(Issue).filter(Issue.status == "Linked").count()
            critical_count = db.query(Issue).filter(Issue.severity == "Critical").count()

            # Issues by status (for chart)
            status_rows = (
                db.query(Issue.status, func.count(Issue.id))
                .group_by(Issue.status)
                .all()
            )
            status_labels = [row[0] or "Unknown" for row in status_rows]
            status_values = [row[1] for row in status_rows]

            # Issues by category (for chart)
            category_rows = (
                db.query(Issue.category, func.count(Issue.id))
                .group_by(Issue.category)
                .all()
            )
            category_labels = [row[0] or "Uncategorized" for row in category_rows]
            category_values = [row[1] for row in category_rows]

            # Daily issues (last 14 days)
            daily_rows = (
                db.query(
                    func.date_trunc("day", Issue.created_at).label("day"),
                    func.count(Issue.id)
                )
                .group_by("day")
                .order_by("day")
                .limit(14)
                .all()
            )
            daily_labels = [row[0].strftime("%d-%b") for row in daily_rows]
            daily_values = [row[1] for row in daily_rows]
    except OperationalError:
        app.logger.exception("DB error in admin_dashboard")
        flash("Database error loading dashboard.", "danger")
        return redirect(url_for("index"))

    return render_template(
        "admin/dashboard.html",
        total_issues=total_issues,
        pending_count=pending_count,
        resolved_count=resolved_count,
        linked_count=linked_count,
        critical_count=critical_count,
        status_labels=status_labels,
        status_values=status_values,
        category_labels=category_labels,
        category_values=category_values,
        daily_labels=daily_labels,
        daily_values=daily_values,
    )


# ------------------------------------------------------
# Admin issues list + assign
# ------------------------------------------------------
@app.route("/admin/issues")
@role_required("admin")
def admin_issues():
    status = request.args.get("status", "all")

    try:
        with SessionLocal() as db:
            q = db.query(Issue).order_by(Issue.created_at.desc())
            if status != "all":
                q = q.filter(Issue.status == status)

            issues = q.all()

            # municipal workers (or officers)
            workers = db.query(User).filter(User.role == "worker").all()
    except OperationalError:
        app.logger.exception("DB error in admin_issues")
        flash("Database error.", "danger")
        return redirect(url_for("admin_dashboard"))

    return render_template(
        "admin/issues.html",
        issues=issues,
        workers=workers,
        selected_status=status,
    )


@app.route("/admin/issues/<int:issue_id>/assign", methods=["POST"])
@role_required("admin")
def assign_issue(issue_id):
    assigned_to = request.form.get("assigned_to")  # worker name or "Unassigned"
    status = request.form.get("status_filter", "all")

    try:
        with SessionLocal() as db:
            issue = db.get(Issue, issue_id)
            if not issue:
                flash("Issue not found.", "danger")
                return redirect(url_for("admin_issues", status=status))

            # you may prefer to store user_id instead, but for now we use name
            issue.assigned_to = assigned_to if assigned_to != "none" else None
            db.commit()
    except OperationalError:
        app.logger.exception("DB error in assign_issue")
        flash("Database error assigning issue.", "danger")
        return redirect(url_for("admin_issues", status=status))

    flash("Issue assigned successfully.", "success")
    return redirect(url_for("admin_issues", status=status))


@app.route("/admin/issues/<int:issue_id>/pdf")
@role_required("admin")
def issue_pdf(issue_id):
    try:
        with SessionLocal() as db:
            issue = db.get(Issue, issue_id)
            if not issue:
                flash("Issue not found.", "danger")
                return redirect(url_for("admin_issues"))
    except OperationalError:
        app.logger.exception("DB error in issue_pdf")
        flash("Database error.", "danger")
        return redirect(url_for("admin_issues"))

    html = render_template("admin/issue_pdf.html", issue=issue)

    if not PDF_AVAILABLE:
        flash("PDF export unavailable (missing package). Serving HTML instead.", "warning")
        return html, 200, {"Content-Type": "text/html; charset=utf-8"}

    # create PDF
    result = BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=result)
    if pisa_status.err:
        app.logger.error("PDF creation failed: %s", pisa_status.err)
        flash("Failed to generate PDF.", "danger")
        return redirect(url_for("admin_issues"))

    pdf = result.getvalue()
    resp = make_response(pdf)
    resp.headers["Content-Type"] = "application/pdf"
    resp.headers["Content-Disposition"] = f"attachment; filename=issue_{issue.id}.pdf"
    return resp


# ------------------------------------------------------
# Map (Leaflet) route
# ------------------------------------------------------
@app.route("/map")
@login_required
def issue_map():
    try:
        with SessionLocal() as db:
            issues = db.query(Issue).all()
    except OperationalError:
        app.logger.exception("DB error in issue_map")
        issues = []

    # Convert for JS rendering
    issue_list = []
    for i in issues:
        issue_list.append({
            "id": i.id,
            "title": (i.issue[:40] + "...") if i.issue else "No description",
            "location": i.location,
            "lat": None,
            "lng": None,
            "status": i.status,
            "category": i.category,
            "upvotes": i.upvotes
        })

    return render_template("map.html", issues=issue_list)


# ------------------------------------------------------
# Run App
# ------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
