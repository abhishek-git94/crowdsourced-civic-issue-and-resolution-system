from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
import language_tool_python

app = Flask(__name__, template_folder='templates', static_folder='static')
app.secret_key = "secret123"  # needed for flash messages

# Connect to your LanguageTool server
tool = language_tool_python.LanguageTool('en-US', remote_server='http://localhost:8081')

def correct_text(text):
    matches = tool.check(text)
    return language_tool_python.utils.correct(text, matches)

# ---------- ROUTES ----------

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/view')
def view_issues():
    # For now, just render a template (you can create view_issues.html later)
    return render_template('view_issues.html')


@app.route('/report', methods=['GET', 'POST'])
def report_issue():
    if request.method == 'POST':
        name = request.form['name']
        issue = request.form['issue']
        location = request.form['location']
        file = request.files.get('attachment')
        if file:
            upload = os.path.join('static', 'uploads', file.filename)
            file.save(upload)   
        # Correct grammar using LanguageTool
        corrected_issue = correct_text(issue)

        flash(f"Issue submitted successfully! Corrected Description: {corrected_issue}", "success")
        # (Later you can save this to your database instead of flashing)

        return redirect(url_for('report_issue'))

    return render_template('report_issues.html')

# API route (for AJAX if needed)
@app.route('/correct', methods=['POST'])
def correct_route():
    data = request.json
    text = data.get("text", "")
    corrected = correct_text(text)
    return jsonify({"corrected_text": corrected})

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
