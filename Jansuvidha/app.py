# at top of app.py
import os
from utils.duplicate_detector import (
    get_local_embedding, get_openai_embedding,
    cosine_similarity, embed_to_json, json_to_embed
)
import json

# Choose backend: "local" or "openai"
EMBED_BACKEND = os.getenv("EMBED_BACKEND", "local")  # or "openai"
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", 0.78))
RECENT_CHECK_COUNT = int(os.getenv("RECENT_CHECK_COUNT", 50))


import os
from flask import (
    Flask, request, render_template, redirect, 
    url_for, flash, jsonify, session )
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime

from database import engine, SessionLocal
from models import Base, User, Issue
from ai_analyzer import CivicAIAnalyzer

# NEW FILES
from auth_blueprint import auth_bp
from auth_helpers import login_required, role_required

# APP INITIALIZATION
app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = os.getenv("SECRET_KEY", "secret123")

# Register authentication blueprint
app.register_blueprint(auth_bp)

# Flask-Migrate
migrate = Migrate(app, Base)

# Auto-create tables ONLY in development
if os.getenv("FLASK_ENV") == "development":
    print("📌 Development Mode → Creating tables locally")
    Base.metadata.create_all(bind=engine)
else:
    print("🚀 Production Mode → No auto-create")


# AI Analyzer
ai_analyzer = CivicAIAnalyzer(
    text_model="llama3",
    yolo_model="yolov8_civic.pt"
)

# -----------------------------------------------------------
# ROUTES
# -----------------------------------------------------------

@app.route('/')
def index():
    return render_template('index.html')


# VIEW ISSUES (login required)
@app.route('/view')
@login_required
def view_issues():
    with SessionLocal() as db:
        issues = db.query(Issue).order_by(Issue.created_at.desc()).all()
    return render_template('view_issues.html', issues=issues)


# UPVOTE ROUTE (fixed)
@app.route('/issue/<int:issue_id>/upvote', methods=['POST'])
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
    return redirect(url_for('view_issues'))

# -----------------------------------------------------------
# REPORT ISSUE (AI-supported)
# -----------------------------------------------------------
# REPORT route (modified)
@app.route('/report', methods=['GET', 'POST'])
@login_required
def report_issue():
    if request.method == 'POST':
        name = session.get("user_name") or request.form.get('name')
        location = request.form.get('location', '')
        file = request.files.get('attachment')

        analysis = None
        file_path = None

        # IMAGE UPLOAD + AI subject detection (keeps your existing logic)
        if file and file.filename:
            uploads_folder = os.path.join(app.static_folder, 'uploads')
            os.makedirs(uploads_folder, exist_ok=True)

            filename = secure_filename(file.filename)
            upload_path = os.path.join(uploads_folder, filename)
            file.save(upload_path)

            file_path = f"uploads/{filename}"

            try:
                analysis = ai_analyzer.analyze_civic_issue(upload_path, location)
                issue_text = analysis.get("description", "(No description)")
            except Exception as e:
                print("⚠️ AI Error:", e)
                issue_text = request.form.get('issue', '(No description)')
        else:
            issue_text = request.form.get('issue', '(No description)')

        # --- Build text for embedding (RAG-friendly)
        # include location, short meta to improve matching
        embed_text = f"{issue_text}\nLocation: {location}"

        # optionally also include detected objects from image to the string
        if analysis and analysis.get('detected_objects'):
            embed_text += "\nObjects: " + ", ".join(analysis.get('detected_objects'))

        # Compute embedding using chosen backend
        try:
            if EMBED_BACKEND == "openai":
                embedding = get_openai_embedding(embed_text)
            else:
                embedding = get_local_embedding(embed_text)
        except Exception as e:
            print("Embedding error:", e)
            embedding = None

        # If we have embedding, check against recent issues
        similar_candidates = []
        if embedding:
            with SessionLocal() as db:
                # fetch last N issues that have embeddings
                rows = db.query(Issue).filter(Issue.embedding != None).order_by(Issue.created_at.desc()).limit(RECENT_CHECK_COUNT).all()
                for r in rows:
                    other_emb = json.loads(r.embedding)
                    sim = cosine_similarity(embedding, other_emb)
                    if sim >= SIMILARITY_THRESHOLD:
                        similar_candidates.append({
                            "id": r.id,
                            "issue": r.issue,
                            "location": r.location,
                            "upvotes": r.upvotes,
                            "created_at": r.created_at,
                            "similarity": round(sim, 3),
                        })

        # If duplicates found → show confirm page
        if similar_candidates:
            # Pass new issue data + candidates to confirmation template
            # Temporarily store new issue data in session to continue after confirmation
            session['_pending_issue'] = {
                "name": name,
                "issue_text": issue_text,
                "location": location,
                "file_path": file_path,
                "analysis": analysis,
                "embedding": embed_to_json(embedding) if embedding else None
            }
            return render_template("auth/confirm_duplicate.html", candidates=similar_candidates, pending=session['_pending_issue'])

        # No duplicates → save as usual
        with SessionLocal() as db:
            new_issue = Issue(
                name=name,
                issue=issue_text,
                location=location,
                file=file_path,
                status="Pending",
                category=analysis["category"] if analysis else None,
                confidence=analysis["confidence"] if analysis else None,
                severity=analysis["severity"] if analysis else None,
                embedding=embed_to_json(embedding) if embedding else None
            )
            db.add(new_issue)
            db.commit()

        flash("Issue reported successfully!", "success")
        return redirect(url_for('report_issue'))

    return render_template('report_issues.html')

# -----------------------------------------------------------
# ADMIN DASHBOARD
# -----------------------------------------------------------
@app.route("/admin")
@role_required("admin")
def admin_dashboard():
    with SessionLocal() as db:
        issues = db.query(Issue).order_by(Issue.created_at.desc()).all()
    return render_template("admin_dashboard.html", issues=issues)


@app.route("/admin/update_status/<int:issue_id>", methods=["POST"])
@role_required("admin")
def update_status(issue_id):
    new_status = request.form.get("status")
    with SessionLocal() as db:
        issue = db.query(Issue).filter_by(id=issue_id).first()
        if issue:
            issue.status = new_status
            db.commit()
            flash("Status updated!", "success")
    return redirect(url_for("admin_dashboard"))

# -----------------------------------------------------------
# MANAGER DASHBOARD
# -----------------------------------------------------------
@app.route("/manager")
@role_required("manager")
def manager_dashboard():
    manager_name = session.get("user_name")

    with SessionLocal() as db:
        assigned = db.query(Issue).filter_by(assigned_to=manager_name).all()

    return render_template("manager_dashboard.html", assigned=assigned)


@app.route("/manager/update/<int:issue_id>", methods=["POST"])
@role_required("manager")
def manager_update(issue_id):
    new_status = request.form.get("status")

    with SessionLocal() as db:
        issue = db.query(Issue).filter_by(id=issue_id).first()
        if issue:
            issue.status = new_status
            db.commit()
            flash("Issue updated.", "success")

    return redirect(url_for("manager_dashboard"))

# -----------------------------------------------------------
# TRENDING ISSUES
# -----------------------------------------------------------
@app.route('/trending')
@login_required
def trending_issues():
    with SessionLocal() as db:
        issues = db.query(Issue).order_by(Issue.upvotes.desc()).limit(5).all()
    return render_template("trending_issues.html", issues=issues)

@app.route('/report/confirm_link', methods=['POST'])
@login_required
def confirm_link():
    """User chose to link pending issue to existing issue."""
    pending = session.pop('_pending_issue', None)
    link_to = int(request.form.get('link_to', 0))
    if not pending or not link_to:
        flash("No pending issue found or target invalid.", "danger")
        return redirect(url_for('report_issue'))

    with SessionLocal() as db:
        # create new issue but mark as duplicate_of
        new_issue = Issue(
            name=pending['name'],
            issue=pending['issue_text'],
            location=pending['location'],
            file=pending['file_path'],
            status="Linked",
            is_duplicate_of=link_to,
            embedding=pending.get('embedding')
        )
        db.add(new_issue)
        db.commit()

    flash("Issue linked to existing report. Thank you!", "success")
    return redirect(url_for('view_issues'))


@app.route('/report/force_create', methods=['POST'])
@login_required
def force_create():
    """User chose to force-create the issue despite similar matches."""
    pending = session.pop('_pending_issue', None)
    if not pending:
        flash("No pending issue to create.", "danger")
        return redirect(url_for('report_issue'))

    with SessionLocal() as db:
        new_issue = Issue(
            name=pending['name'],
            issue=pending['issue_text'],
            location=pending['location'],
            file=pending['file_path'],
            status="Pending",
            embedding=pending.get('embedding')
        )
        db.add(new_issue)
        db.commit()

    flash("Issue created successfully.", "success")
    return redirect(url_for('view_issues'))

# -----------------------------------------------------------
# API: AI ANALYSIS ENDPOINT
# -----------------------------------------------------------
@app.route('/analyze-image', methods=['POST'])
def analyze_image_api():
    try:
        if 'image' not in request.files:
            return jsonify({"error": "No image provided"}), 400

        file = request.files['image']
        location = request.form.get('location', 'Unknown location')

        if not file.filename:
            return jsonify({"error": "No file selected"}), 400

        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_name = f"temp_{timestamp}_{filename}"

        uploads_folder = os.path.join(app.static_folder, 'uploads')
        os.makedirs(uploads_folder, exist_ok=True)

        temp_path = os.path.join(uploads_folder, temp_name)
        file.save(temp_path)

        result = ai_analyzer.analyze_civic_issue(temp_path, location)

        return jsonify({
            "success": True,
            "description": result['description'],
            "category": result['category'],
            "confidence": result['confidence'],
            "severity": result['severity'],
            "detected_objects": result['detected_objects'][:5]
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -----------------------------------------------------------
# ENTRY POINT
# -----------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
