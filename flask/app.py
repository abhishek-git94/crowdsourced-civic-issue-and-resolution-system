from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/report', methods=['GET', 'POST'])
def report_issue():
    if request.method == 'POST':
        name = request.form['name']
        issue = request.form['issue']
        location = request.form['location']
        print(f"Issue reported by {name}: {issue} at {location}")
        return redirect(url_for('view_issues'))
    return render_template('report_issue.html')

@app.route('/issues')
def view_issues():
    issues = [
        {'name': 'Rohit', 'issue': 'Pothole on MG Road', 'status': 'Pending'},
        {'name': 'Sneha', 'issue': 'Garbage not collected', 'status': 'In Progress'}
    ]
    return render_template('view_issues.html', issues=issues)

if __name__ == '__main__':
    app.run(debug=True)
