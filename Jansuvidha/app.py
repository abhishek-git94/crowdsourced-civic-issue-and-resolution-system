from flask import Flask, request, render_template, redirect, url_for, flash
import os
from sqlalchemy import select
from database import engine, SessionLocal
from models import Base, Issue

# ✅ Create your Flask app FIRST
app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = "secret123"

# ✅ Then initialize DB (after app exists)
Base.metadata.create_all(bind=engine)


# ---------- ROUTES ----------

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/view')
def view_issues():
    with SessionLocal() as db:
        issues = db.query(Issue).order_by(Issue.created_at.desc()).all()
        return render_template('view_issues.html', issues=issues)


@app.route('/report', methods=['GET', 'POST'])
def report_issue():
    if request.method == 'POST':
        name = request.form.get('name', '')
        issue_text = request.form.get('issue', '')
        location = request.form.get('location', '')
        file = request.files.get('attachment')

        if file and file.filename:
            uploads_folder = os.path.join(app.static_folder, 'uploads')
            os.makedirs(uploads_folder, exist_ok=True)
            upload_path = os.path.join(uploads_folder, file.filename)
            file.save(upload_path)
            file_path = f"uploads/{file.filename}"
        else:
            file_path = None

        # ✅ Save to DB
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


# ---------- TEST ROUTE ----------
@app.route("/db-test")
def db_test():
    try:
        with engine.connect() as conn:
            result = conn.execute(select(1))
            return "✅ Database connected successfully!"
    except Exception as e:
        return f"❌ Database connection failed: {e}"


# ---------- ENTRY POINT ----------
if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
