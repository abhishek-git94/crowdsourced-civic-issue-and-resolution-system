import os
from flask import (
    Flask, request, render_template, redirect, 
    url_for, flash, jsonify, session
)
from flask_migrate import Migrate
from sqlalchemy import select
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime

from database import engine, SessionLocal
from models import Base, User, Issue
from ai_analyzer import CivicAIAnalyzer

# NEW FILES
from auth_blueprint import auth_bp
from auth_helpers import login_required, role_required

# -----------------------------
# APP INITIALIZATION
# -----------------------------
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

# -----------------------------
# ROUTES
# -----------------------------

@app.route('/')
def index():
    return render_template('index.html')

# VIEW ISSUES (login required)
@app.route('/view')
@login_required
def view_issues():
    """Show all reported issues."""
    with SessionLocal() as db:
        issues = db.query(Issue).order_by(Issue.created_at.desc()).all()
    return render_template('view_issues.html', issues=issues)

# REPORT ISSUE (AI-supported)
@app.route('/report', methods=['GET', 'POST'])
@login_required
def report_issue():
    if request.method == 'POST':
        name = session.get("user_name") or request.form.get('name')
        location = request.form.get('location', '')
        file = request.files.get('attachment')

        analysis = None
        file_path = None

        # -----------------------------
        # IMAGE UPLOAD
        # -----------------------------
        if file and file.filename:
            uploads_folder = os.path.join(app.static_folder, 'uploads')
            os.makedirs(uploads_folder, exist_ok=True)

            filename = secure_filename(file.filename)
            upload_path = os.path.join(uploads_folder, filename)
            file.save(upload_path)

            file_path = f"uploads/{filename}"

            # -----------------------------
            # AI ANALYSIS PIPELINE
            # -----------------------------
            try:
                analysis = ai_analyzer.analyze_civic_issue(upload_path, location)
                issue_text = analysis["description"]
            except Exception as e:
                print("⚠️ AI Error:", e)
                issue_text = "(AI could not analyze this image)"
        else:
            issue_text = request.form.get('issue', '(No description)')

        # -----------------------------
        # SAVE ISSUE
        # -----------------------------
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
            )
            db.add(new_issue)
            db.commit()

        flash("Issue reported successfully!", "success")
        return redirect(url_for('report_issue'))

    return render_template('report_issues.html')


# -----------------------------
# ADMIN DASHBOARD
# -----------------------------
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


# -----------------------------
# MANAGER DASHBOARD
# -----------------------------
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


# -----------------------------
# API: AI ANALYSIS ENDPOINT
# -----------------------------
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


# -----------------------------
# ENTRY POINT
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)