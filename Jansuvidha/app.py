import os
import json
from datetime import datetime
from flask import (
    Flask, request, render_template, redirect,
    url_for, flash, jsonify, session
)
from werkzeug.utils import secure_filename

from database import engine, SessionLocal
from models import Base, User, Issue
from ai_analyzer import CivicAIAnalyzer

from utils.duplicate_detector import (
    get_local_embedding, get_openai_embedding,
    cosine_similarity, embed_to_json
)

from auth_blueprint import auth_bp
from auth_helpers import login_required, role_required

# ------------------------------------------------------
# CONFIG
# ------------------------------------------------------
app = Flask(__name__, template_folder="templates", static_folder="static")
app.secret_key = os.getenv("SECRET_KEY", "secret123")

app.register_blueprint(auth_bp)

# Ensure upload directory exists
os.makedirs(os.path.join(app.static_folder, "uploads"), exist_ok=True)

# Duplicate detection settings
EMBED_BACKEND = os.getenv("EMBED_BACKEND", "local")
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", 0.78))
RECENT_CHECK_COUNT = int(os.getenv("RECENT_CHECK_COUNT", 50))

# AI Analyzer
ai_analyzer = CivicAIAnalyzer(
    text_model="llama3",
    yolo_model="yolov8_civic.pt"
)

print("SQLAlchemy engine ready to go!")

# ------------------------------------------------------
# ROUTES
# ------------------------------------------------------

@app.route("/")
def index():
    return render_template("index.html")

# ------------------------------------------------------
# View Issues
# ------------------------------------------------------
@app.route("/view")
@login_required
def view_issues():
    with SessionLocal() as db:
        issues = db.query(Issue).order_by(Issue.created_at.desc()).all()
    return render_template("view_issues.html", issues=issues)

# ------------------------------------------------------
# Upvote
# ------------------------------------------------------
@app.route("/issue/<int:issue_id>/upvote", methods=["POST"])
@login_required
def upvote_issue(issue_id):
    with SessionLocal() as db:
        issue = db.query(Issue).filter_by(id=issue_id).first()
        if issue:
            issue.upvotes += 1
            db.commit()
            flash("You have upvoted this issue!", "success")
        else:
            flash("Issue not found.", "danger")

    return redirect(url_for("view_issues"))

# ------------------------------------------------------
# REPORT ISSUE
# ------------------------------------------------------
@app.route("/report", methods=["GET", "POST"])
@login_required
def report_issue():
    if request.method == "POST":

        name = session.get("user_name")
        location = request.form.get("location", "")
        file = request.files.get("attachment")

        analysis = None
        file_path = None

        # Upload image
        if file and file.filename:
            uploads_dir = os.path.join(app.static_folder, "uploads")
            filename = secure_filename(file.filename)
            full_path = os.path.join(uploads_dir, filename)
            file.save(full_path)
            file_path = f"uploads/{filename}"

            try:
                analysis = ai_analyzer.analyze_civic_issue(full_path, location)
                issue_text = analysis.get("description", "")
            except Exception as e:
                print("AI ERROR:", e)
                issue_text = request.form.get("issue", "")
        else:
            issue_text = request.form.get("issue", "")

        # Embedding text
        embed_text = f"{issue_text}\nLocation: {location}"
        if analysis and analysis.get("detected_objects"):
            embed_text += "\nObjects: " + ", ".join(analysis["detected_objects"])

        try:
            embedding = (
                get_openai_embedding(embed_text)
                if EMBED_BACKEND == "openai"
                else get_local_embedding(embed_text)
            )
        except:
            embedding = None

        # -------------------------------------------
        # CHECK DUPLICATES
        # -------------------------------------------
        similar = []
        if embedding:
            with SessionLocal() as db:
                recent = (
                    db.query(Issue)
                    .filter(Issue.embedding != None)
                    .order_by(Issue.created_at.desc())
                    .limit(RECENT_CHECK_COUNT)
                    .all()
                )

            for old in recent:
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

        # If duplicates are found
        if similar:
            session["_pending_issue"] = {
                "name": name,
                "issue": issue_text,
                "location": location,
                "file_path": file_path,
                "analysis": analysis,
                "embedding": embed_to_json(embedding)
            }
            return render_template("confirm_duplicate.html",
                                   candidates=similar,
                                   pending=session["_pending_issue"])

        # Save normally
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
                user_id=session.get("user_id")
            )
            db.add(new_issue)
            db.commit()

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
        flash("Missing pending issue.", "danger")
        return redirect(url_for("report_issue"))

    with SessionLocal() as db:
        new_issue = Issue(
            name=pending["name"],
            issue=pending["issue"],
            location=pending["location"],
            file=pending["file_path"],
            status="Linked",
            is_duplicate_of=link_to,
            embedding=pending.get("embedding"),
            user_id=session.get("user_id")
        )
        db.add(new_issue)
        db.commit()

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

    with SessionLocal() as db:
        new_issue = Issue(
            name=pending["name"],
            issue=pending["issue"],
            location=pending["location"],
            file=pending["file_path"],
            status="Pending",
            embedding=pending.get("embedding"),
            user_id=session.get("user_id")
        )
        db.add(new_issue)
        db.commit()

    flash("Issue created successfully.", "success")
    return redirect(url_for("view_issues"))

# ------------------------------------------------------
# AI API
# ------------------------------------------------------
@app.route("/analyze-image", methods=["POST"])
def analyze_image_api():
    try:
        file = request.files.get("image")
        location = request.form.get("location", "Unknown")

        if not file or not file.filename:
            return jsonify({"error": "No image provided"}), 400

        uploads = os.path.join(app.static_folder, "uploads")
        filename = f"tmp_{datetime.now().timestamp()}_{secure_filename(file.filename)}"
        path = os.path.join(uploads, filename)
        file.save(path)

        result = ai_analyzer.analyze_civic_issue(path, location)

        return jsonify({
            "success": True,
            "description": result["description"],
            "category": result["category"],
            "confidence": result["confidence"],
            "severity": result["severity"],
            "detected_objects": result["detected_objects"][:5]
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/trending')
@login_required
def trending_issues():
    with SessionLocal() as db:
        issues = db.query(Issue).order_by(Issue.upvotes.desc()).limit(5).all()
    return render_template("trending_issues.html", issues=issues)

# ------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
