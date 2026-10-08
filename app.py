import os
import re
from datetime import datetime
from functools import wraps

from bson import ObjectId
from bson.errors import InvalidId
from flask import Flask, request, render_template, redirect, url_for, send_from_directory, session, abort, jsonify, flash
from flask_bcrypt import Bcrypt
from pymongo import MongoClient
from werkzeug.utils import secure_filename

import config

# Flask app setup
app = Flask(__name__)
app.secret_key = config.SECRET_KEY
app.config['MAX_CONTENT_LENGTH'] = config.MAX_UPLOAD_MB * 1024 * 1024
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
bcrypt = Bcrypt(app)

# Configure Google Generative AI (chatbot is disabled if no key is set)
genai = None
if config.GEMINI_API_KEY:
    import google.generativeai as genai
    genai.configure(api_key=config.GEMINI_API_KEY)

# Database setup (MongoDB). CRV holds students, TRV holds faculty.
client = MongoClient(config.MONGODB_URI, serverSelectionTimeoutMS=5000)
db = client['CRV']
tb = client['TRV']

# Set upload folder path
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
ROADMAP_FOLDER = os.path.join(BASE_DIR, 'static', 'roadmaps')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Blocked so uploaded files can't be served back as runnable pages/scripts
BLOCKED_EXTENSIONS = {'html', 'htm', 'js', 'php', 'exe', 'bat', 'sh', 'svg'}

EMAIL_RE = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')

# Course catalogue shown on Home and Courses (static demo content)
COURSES = [
    {'title': 'Complete HTML tutorial', 'tutor': 'John Deo', 'date': '21-10-2022', 'thumb': 'thumb-1.png', 'avatar': 'pic-2.jpg', 'videos': 10},
    {'title': 'Complete CSS tutorial', 'tutor': 'John Deo', 'date': '21-10-2022', 'thumb': 'thumb-2.png', 'avatar': 'pic-3.jpg', 'videos': 10},
    {'title': 'Complete JavaScript tutorial', 'tutor': 'John Deo', 'date': '21-10-2022', 'thumb': 'thumb-3.png', 'avatar': 'pic-4.jpg', 'videos': 10},
    {'title': 'Complete Bootstrap tutorial', 'tutor': 'John Deo', 'date': '21-10-2022', 'thumb': 'thumb-4.png', 'avatar': 'pic-5.jpg', 'videos': 10},
    {'title': 'Complete jQuery tutorial', 'tutor': 'John Deo', 'date': '21-10-2022', 'thumb': 'thumb-5.png', 'avatar': 'pic-6.jpg', 'videos': 10},
    {'title': 'Complete SASS tutorial', 'tutor': 'John Deo', 'date': '21-10-2022', 'thumb': 'thumb-6.png', 'avatar': 'pic-7.jpg', 'videos': 10},
    {'title': 'Complete PHP tutorial', 'tutor': 'John Deo', 'date': '21-10-2022', 'thumb': 'thumb-7.png', 'avatar': 'pic-8.jpg', 'videos': 10},
    {'title': 'Complete MySQL tutorial', 'tutor': 'John Deo', 'date': '21-10-2022', 'thumb': 'thumb-8.png', 'avatar': 'pic-9.jpg', 'videos': 10},
    {'title': 'Complete React tutorial', 'tutor': 'John Deo', 'date': '21-10-2022', 'thumb': 'thumb-9.png', 'avatar': 'pic-1.jpg', 'videos': 10},
]

# Short labels for roadmap files whose title isn't just the file name
ROADMAP_LABELS = {'cpp': 'C++', 'ios': 'iOS', 'qa': 'QA', 'mlops': 'MLOps', 'devops': 'DevOps',
                  'devrel': 'DevRel', 'api-design': 'API Design', 'git-github': 'Git & GitHub',
                  'javascript': 'JavaScript', 'postgresql-dba': 'PostgreSQL DBA', 'ai-engineer': 'AI Engineer',
                  'ai-data-scientist': 'AI Data Scientist'}


def get_roadmaps():
    """List roadmap PDFs that actually exist on disk (no broken links)."""
    items = []
    for name in sorted(os.listdir(ROADMAP_FOLDER)):
        if name.lower().endswith('.pdf'):
            slug = name[:-4]
            title = ROADMAP_LABELS.get(slug, slug.replace('-', ' ').title())
            items.append({'title': title, 'file': name})
    return items


def file_extension(filename):
    return filename.rsplit('.', 1)[1].lower() if '.' in filename else ''


def allowed_file(filename):
    """Allow any document/media type except a small blocklist of executable/web files."""
    return bool(filename) and file_extension(filename) not in BLOCKED_EXTENSIONS


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to continue.', 'error')
            return redirect(url_for('login_register'))
        return view(*args, **kwargs)
    return wrapped


@app.context_processor
def inject_user():
    """Make the logged-in user's name and role available in every template."""
    return {
        'username': session.get('username', 'Guest'),
        'role': session.get('role', 'student'),
        'current_year': datetime.now().year,
    }


# Routes
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('home'))
    return redirect(url_for('login_register'))


@app.route('/home')
@login_required
def home():
    return render_template('home.html', courses=COURSES[:6], roadmaps=get_roadmaps()[:8])


@app.route('/auth', methods=['GET', 'POST'])
def login_register():
    if request.method == 'POST':
        action = request.form.get('action')  # Determine whether login or register
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')

        if action == 'login':
            if not email or not password:
                flash('Please enter your email and password.', 'error')
                return redirect(url_for('login_register'))

            # Check if user exists in both databases
            user = db.users.find_one({"email": email}) or tb.users.find_one({"email": email})
            if user and bcrypt.check_password_hash(user['password'], password):
                session.clear()
                session['user_id'] = str(user['_id'])
                session['username'] = user['username']
                session['role'] = user.get('role', 'student')
                return redirect(url_for('home'))

            flash('Invalid email or password. Please try again.', 'error')
            return redirect(url_for('login_register'))

        elif action == 'register':
            username = request.form.get('username', '').strip()
            role = request.form.get('role')

            if not (2 <= len(username) <= 40):
                flash('Username must be between 2 and 40 characters.', 'error')
            elif not EMAIL_RE.match(email):
                flash('Please enter a valid email address.', 'error')
            elif len(password) < 6:
                flash('Password must be at least 6 characters.', 'error')
            elif role not in ('student', 'faculty'):
                flash('Invalid role selected. Please choose either Student or Faculty.', 'error')
            elif db.users.find_one({"email": email}) or tb.users.find_one({"email": email}):
                flash('Email already exists. Please try another one.', 'error')
            else:
                hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
                user_data = {
                    "username": username,
                    "email": email,
                    "password": hashed_password,
                    "role": role,
                }
                # Insert into the appropriate database based on role
                (db if role == 'student' else tb).users.insert_one(user_data)
                flash('Registration successful! Please log in.', 'success')
                return redirect(url_for('login_register'))

            return redirect(url_for('login_register', mode='register'))

    return render_template('auth.html', mode=request.args.get('mode', 'login'))


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login_register'))


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if session.get('role') != 'faculty':
        abort(403)

    if request.method == 'POST':
        file = request.files.get('file')
        if not file or not file.filename:
            flash('Please choose a file to upload.', 'error')
            return redirect(url_for('upload'))
        filename = secure_filename(file.filename)
        if not filename or not allowed_file(filename):
            flash('This file type is not allowed.', 'error')
            return redirect(url_for('upload'))

        # Add a timestamp so files with the same name don't overwrite each other
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        stem, ext = os.path.splitext(filename)
        new_filename = f'{stem}_{timestamp}{ext}'
        file.save(os.path.join(UPLOAD_FOLDER, new_filename))
        flash(f'"{filename}" uploaded successfully.', 'success')
        return redirect(url_for('download'))

    return render_template('upload.html', max_mb=config.MAX_UPLOAD_MB)


@app.route('/download')
@login_required
def download():
    files = []
    for name in sorted(os.listdir(UPLOAD_FOLDER)):
        path = os.path.join(UPLOAD_FOLDER, name)
        if os.path.isfile(path):
            files.append({
                'name': name,
                'size_kb': max(1, os.path.getsize(path) // 1024),
                'ext': file_extension(name) or 'file',
            })
    return render_template('download.html', files=files)


@app.route('/download/<path:filename>')
@login_required
def download_file(filename):
    # send_from_directory rejects paths that escape UPLOAD_FOLDER
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)


@app.route('/profile')
@login_required
def profile():
    return redirect(url_for('dashboard'))


@app.route('/roadmap')
@login_required
def roadmap():
    return render_template('road.html', roadmaps=get_roadmaps())


@app.route('/courses')
@login_required
def courses():
    return render_template('courses.html', courses=COURSES)


@app.route('/playlist')
@login_required
def playlist():
    return render_template('playlist.html', course=COURSES[0])


# Comment section route for video
@app.route('/video', methods=['GET', 'POST'])
@login_required
def video():
    if request.method == 'POST':
        comment_text = request.form.get('comment', '').strip()
        if not comment_text:
            flash('Comment cannot be empty.', 'error')
        elif len(comment_text) > 1000:
            flash('Comment is too long (max 1000 characters).', 'error')
        else:
            db.comments.insert_one({
                'user_id': session.get('user_id'),
                'username': session.get('username'),
                'text': comment_text,
                'timestamp': datetime.now()
            })
            flash('Comment added.', 'success')
        # Redirect to avoid resubmitting the form on page refresh
        return redirect(url_for('video') + '#comments')

    comments = list(db.comments.find().sort('timestamp', -1).limit(100))
    return render_template('watch-video.html', comments=comments)


@app.route('/dashboard')
@login_required
def dashboard():
    comment_count = db.comments.count_documents({'user_id': session.get('user_id')})
    return render_template('dashboard.html', comment_count=comment_count)


@app.route('/dashboard/chatbot')
@login_required
def chatbot():
    return render_template('chatbot.html', chatbot_enabled=genai is not None)


@app.route('/dashboard/generate-response', methods=['POST'])
def generate_response():
    if 'user_id' not in session:
        return jsonify({'error': 'Please log in to use the chatbot.'}), 401
    if genai is None:
        return jsonify({'error': 'Chatbot is not configured. Set GEMINI_API_KEY on the server.'}), 503

    user_input = (request.form.get('user_input') or '').strip()
    if not user_input:
        return jsonify({'error': 'No input provided'}), 400
    if len(user_input) > 4000:
        return jsonify({'error': 'Message is too long (max 4000 characters).'}), 400
    try:
        model = genai.GenerativeModel(model_name=config.GEMINI_MODEL)
        response = model.generate_content(user_input)
        return jsonify({'response': response.text})
    except Exception:
        app.logger.exception('Gemini request failed')
        return jsonify({'error': 'Sorry, the assistant could not respond right now. Please try again.'}), 502


# Route for deleting comments (faculty only)
@app.route('/delete_comment/<comment_id>', methods=['POST'])
@login_required
def delete_comment(comment_id):
    if session.get('role') != 'faculty':
        abort(403)
    try:
        result = db.comments.delete_one({'_id': ObjectId(comment_id)})
    except InvalidId:
        result = None
    if result and result.deleted_count:
        flash('Comment deleted successfully', 'success')
    else:
        flash('Comment not found', 'error')
    return redirect(url_for('video') + '#comments')


# Error handling
@app.errorhandler(403)
def forbidden(e):
    return render_template('error.html', code=403, message="You don't have permission to view this page."), 403


@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', code=404, message="We couldn't find the page you were looking for."), 404


@app.errorhandler(413)
def too_large(e):
    flash(f'File is too large. Maximum size is {config.MAX_UPLOAD_MB} MB.', 'error')
    return redirect(url_for('upload'))


@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', code=500, message="Something went wrong on our side. Please try again."), 500


if __name__ == '__main__':
    app.run(debug=config.DEBUG)
