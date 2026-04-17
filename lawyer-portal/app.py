from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.secret_key = "your_secret_key_here"

# ---------------- Upload Folder ----------------
UPLOAD_FOLDER = os.path.join('static', 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ---------------- In-Memory "Database" ----------------
users = {}  # username: password
cases = []  # list of case dictionaries

# ---------------- Routes ----------------

# Home / Landing Page
@app.route('/')
def home_page():
    return render_template('home.html')

@app.route('/index')
def index_page():
    return render_template('index.html')

# User Registration
@app.route('/register', methods=['GET', 'POST'])
def register_page():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users:
            flash('Username already exists!', 'danger')
            return redirect(url_for('register_page'))
        users[username] = password
        flash('Registration successful!', 'success')
        return redirect(url_for('login_page'))
    return render_template('register.html')

# User Login
@app.route('/login', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and users[username] == password:
            return redirect(url_for('dashboard_page', username=username))
        flash('Invalid username or password!', 'danger')
        return redirect(url_for('login_page'))
    return render_template('login.html')

# Dashboard
@app.route('/dashboard/<username>')
def dashboard_page(username):
    user_cases = [c for c in cases if c['owner'] == username]
    return render_template('dashboard.html', username=username, cases=user_cases)

# Add Case
@app.route('/add_case/<username>', methods=['GET', 'POST'])
def add_case_page(username):
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        client_name = request.form['client_name']
        client_phone = request.form['client_phone']

        # Multiple file upload support
        uploaded_files = request.files.getlist('files')
        filenames = []
        for file in uploaded_files:
            if file and file.filename != '':
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                filenames.append(filename)

        case = {
            'owner': username,
            'title': title,
            'description': description,
            'client_name': client_name,
            'client_phone': client_phone,
            'files': filenames
        }
        cases.append(case)
        flash('Case added successfully!', 'success')
        return redirect(url_for('dashboard_page', username=username))
    return render_template('add_cases.html', username=username)

# View Case
@app.route('/view_case/<int:case_id>/<username>')
def view_case_page(case_id, username):
    if 0 <= case_id < len(cases):
        case = cases[case_id]
        return render_template('view_cases.html', case=case, username=username)
    flash('Case not found!', 'danger')
    return redirect(url_for('dashboard_page', username=username))

# ---------------- Run App ----------------
if __name__ == '__main__':
    app.run(debug=True)
