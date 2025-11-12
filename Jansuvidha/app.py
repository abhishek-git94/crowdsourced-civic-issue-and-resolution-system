from flask import Flask, request, render_template, redirect, url_for, flash, jsonify
# app.py
from flask import Flask, request, render_template, redirect, url_for, flash
import os
from sqlalchemy import select
from database import engine, SessionLocal
from models import Base, Issue
from ai_analyzer import CivicAIAnalyzer

# ------------------------------------------------------------
# ✅ Initialize Flask App
# ------------------------------------------------------------
app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = "secret123"

# ✅ Initialize AI Analyzer (Ollama + YOLO)
ai_analyzer = CivicAIAnalyzer(text_model="llama3")  # Using Llama3 model

# ✅ Initialize database
Base.metadata.create_all(bind=engine)


# ------------------------------------------------------------
# ✅ ROUTES
# ------------------------------------------------------------

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/view')
def view_issues():
    """Show all reported civic issues."""
    with SessionLocal() as db:
        issues = db.query(Issue).order_by(Issue.created_at.desc()).all()
        return render_template('view_issues.html', issues=issues)


@app.route('/report', methods=['GET', 'POST'])
def report_issue():
    """Report a new issue (AI auto-fills description from image)."""
    if request.method == 'POST':
        name = request.form.get('name', '')
        location = request.form.get('location', '')
        file = request.files.get('attachment')

        # --- AI Image Analyzer ---
        if file and file.filename:
            uploads_folder = os.path.join(app.static_folder, 'uploads')
            os.makedirs(uploads_folder, exist_ok=True)
            upload_path = os.path.join(uploads_folder, file.filename)
            file.save(upload_path)
            file_path = f"uploads/{file.filename}"

            try:
                # Step 1: detect objects using YOLO
                detected_objects = ai_analyzer.analyze_image(upload_path)
                # Step 2: generate issue description with Ollama (Llama3)
                issue_text = ai_analyzer.generate_description(detected_objects)
            except Exception as e:
                print("⚠️ AI analysis failed:", e)
                issue_text = "(AI could not analyze image)"
        else:
            file_path = None
            issue_text = request.form.get('issue', '')

        # ✅ Save to database
        with SessionLocal() as db:
            new_issue = Issue(
                name=name,
                issue=issue_text,
                location=location,
                file=file_path,
                status="Pending"
            )
            db.add(new_issue)
            db.commit()

        flash(f"Issue reported successfully by {name} at {location}.", "success")
        return redirect(url_for('report_issue'))

    return render_template('report_issues.html')


# ------------------------------------------------------------
# ✅ TEST ROUTES
# ------------------------------------------------------------

@app.route("/db-test")
def db_test():
    """Quick database connection test."""
    try:
        with engine.connect() as conn:
            conn.execute(select(1))
            return "✅ Database connected successfully!"
    except Exception as e:
        return f"❌ Database connection failed: {e}"


@app.route("/ai-test")
def ai_test():
    """Quick Ollama + Llama3 model test."""
    try:
        result = ai_analyzer.generate_description(["pothole", "garbage"])
        return f"✅ AI working: {result}"
    except Exception as e:
        return f"❌ AI error: {e}"
    
@app.route('/analyze-image', methods=['POST'])
def analyze_image_api():
    """API endpoint for AI image analysis"""
    try:
        if 'image' not in request.files:
            return jsonify({"error": "No image provided"}), 400
        
        file = request.files['image']
        location = request.form.get('location', 'Unknown location')
        
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        # Save temporarily
        from werkzeug.utils import secure_filename
        from datetime import datetime
        
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_filename = f"temp_{timestamp}_{filename}"
        
        uploads_folder = os.path.join(app.static_folder, 'uploads')
        os.makedirs(uploads_folder, exist_ok=True)
        temp_path = os.path.join(uploads_folder, temp_filename)
        
        file.save(temp_path)
        
        # Analyze with AI
        try:
            result = ai_analyzer.analyze_civic_issue(temp_path, location)
            
            return jsonify({
                "success": True,
                "description": result['description'],
                "category": result['category'],
                "confidence": result['confidence'],
                "severity": result.get('severity', 'medium'),
                "detected_objects": result['detected_objects'][:5]
            })
        
        except Exception as e:
            # Clean up on error
            if os.path.exists(temp_path):
                os.remove(temp_path)
            return jsonify({"error": f"AI analysis failed: {str(e)}"}), 500
    
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500


# ------------------------------------------------------------
# ✅ ENTRY POINT
# ------------------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
