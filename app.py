import os
from flask import Flask, request, render_template, redirect, url_for, send_from_directory, session, abort, jsonify, flash
from werkzeug.utils import secure_filename
from datetime import datetime
from flask_bcrypt import Bcrypt
from pymongo import MongoClient
import google.generativeai as genai
import config
from bson import ObjectId
import json
# Flask app setup
app = Flask(__name__)
app.secret_key = config.SECRET_KEY
bcrypt = Bcrypt(app)

# Configure API Key for Google Generative AI
genai.configure(api_key=config.GEMINI_API_KEY)

# Database setup (MongoDB)
client = MongoClient(config.MONGODB_URI)
db = client['CRV']
tb = client['TRV']

# Set upload folder path
BASE_DIR = os.path.abspath(os.path.dirname(__file__))  # Path to the directory containing app.py
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')      # Upload directory
os.makedirs(UPLOAD_FOLDER, exist_ok=True)              # Ensure the directory exists

ALLOWED_EXTENSIONS = None  # Allow all file types

# Helper function to check allowed files
def allowed_file(filename):
    """Check if the file is allowed. If ALLOWED_EXTENSIONS is None, all files are allowed."""
    if ALLOWED_EXTENSIONS is None:
        return True
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Routes
@app.route('/')
def index():
    return redirect(url_for('login_register'))

@app.route('/home')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login_register'))
    username = session.get('username', 'Guest')
    role = session.get('role', 'student')
    return render_template('home.html', username=username, role=role)

from flask import flash
@app.route('/auth', methods=['GET', 'POST'])
def login_register():
    if request.method == 'POST':
        action = request.form.get('action')  # Determine whether login or register

        if action == 'login':
            email = request.form['email']
            password = request.form['password']

            # Check if user exists in both databases
            user = db.users.find_one({"email": email}) or tb.users.find_one({"email": email})
            if user and bcrypt.check_password_hash(user['password'], password):
                session['user_id'] = str(user['_id'])
                session['username'] = user['username']
                session['role'] = user.get('role', 'Unknown')  # Save role in session
                return redirect(url_for('home'))

            # Flash message for invalid credentials
            flash('Invalid email or password. Please try again.', 'error')
            return redirect(url_for('login_register'))  # Redirect back to the login page

        elif action == 'register':
            username = request.form['username']
            email = request.form['email']
            password = request.form['password']
            role = request.form['role']  # Retrieve role (student/faculty) from form


            # Check if email already exists in either database
            if db.users.find_one({"email": email}) or tb.users.find_one({"email": email}):
                flash('Email already exists. Please try another one.', 'error')
                return redirect(url_for('login_register'))

            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            user_data = {
                "username": username,
                "email": email,
                "password": hashed_password,
                "role": role,
            }

            # Insert into the appropriate database based on role
            if role == 'student':
                db.users.insert_one(user_data)
            elif role == 'faculty':
                tb.users.insert_one(user_data)
            else:
                flash('Invalid role selected. Please choose either Student or Faculty.', 'error')
                return redirect(url_for('login_register'))

            # Redirect to the login page after successful registration
            flash('Registration successful! Please log in.', 'success')
            return redirect(url_for('login_register'))

    # Render the registration and login page
    return render_template('auth.html')

    # Render the registration and login page
    return render_template('auth.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login_register'))

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'user_id' not in session or session.get('role') != 'faculty':
        return abort(403, "Access forbidden: Only faculty can upload files.")

    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            new_filename = f'{filename.rsplit(".", 1)[0]}_{timestamp}.{filename.rsplit(".", 1)[1]}'
            save_location = os.path.join(UPLOAD_FOLDER, new_filename)
            file.save(save_location)
            return redirect(url_for('download'))

    return render_template('upload.html')

@app.route('/download')
def download():
    if 'user_id' not in session:
        return redirect(url_for('login_register'))

    files = os.listdir(UPLOAD_FOLDER)
    role = session.get('role', 'student')  # Default to 'student'
    return render_template('download.html', files=files, role=role)

@app.route('/download/<filename>')
def download_file(filename):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    if os.path.isfile(file_path) and file_path.startswith(os.path.abspath(UPLOAD_FOLDER)):
        return send_from_directory(UPLOAD_FOLDER, filename)
    else:
        return f"File '{filename}' not found.", 404

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/roadmap')
def roadmap():
    return render_template('road.html')

@app.route('/courses')
def courses():
    role = session.get('role', 'student')
    return render_template('courses.html', role=role)

@app.route('/playlist')
def playlist():
    role = session.get('role', 'student')
    return render_template('playlist.html', role=role)

# Comment section route for video
@app.route('/video', methods=['GET', 'POST'])
def video():
    if 'user_id' not in session:
        return redirect(url_for('login_register'))

    # Handle comment submission
    if request.method == 'POST':
        user_id = session.get('user_id')
        username = session.get('username')
        comment_text = request.form['comment']

        # Save comment to the database (MongoDB)
        comment_data = {
            'user_id': user_id,
            'username': username,
            'text': comment_text,
            'timestamp': datetime.now()
        }
        db.comments.insert_one(comment_data)  # Store comment in the comments collection

        # Redirect to avoid resubmitting the form on page refresh
        return redirect(url_for('video'))  # Redirect to the same page after POST request

    # Retrieve all comments from the database
    comments = db.comments.find().sort('timestamp', -1)  # Sort by newest first
    role = session.get('role', 'student')
    return render_template('watch-video.html', comments=comments, role=role)

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login_register'))
    username = session.get('username', 'Guest')
    role = session.get('role', 'student')
    return render_template('dashboard.html', username=username, role=role)

@app.route('/dashboard/chatbot')
def chatbot():
    if 'user_id' not in session:
        return redirect(url_for('login_register'))
    return render_template('chatbot.html')

@app.route('/dashboard/generate-response', methods=['POST'])
def generate_response():
    user_input = request.form.get('user_input')
    if user_input:
        try:
            model = genai.GenerativeModel(model_name="gemini-1.5-flash")
            response = model.generate_content(user_input)
            return jsonify({'response': response.text})
        except Exception as e:
            return jsonify({'error': f"Error generating response: {e}"})
    return jsonify({'error': 'No input provided'})

# Route for deleting comments
@app.route('/delete_comment/<comment_id>', methods=['POST'])
def delete_comment(comment_id):
    if 'user_id' not in session:
        return redirect(url_for('login_register'))
    
    role = session.get('role')

    if role != 'faculty':  # If the user is not faculty, redirect
        return redirect(url_for('video'))  # Or show an error message

    # Find and delete the comment by its ID
    comment = db.comments.find_one({'_id': ObjectId(comment_id)})
    if comment:
        db.comments.delete_one({'_id': ObjectId(comment_id)})
        flash('Comment deleted successfully', 'success')  # Flash message on successful deletion
    else:
        flash('Comment not found', 'error')  # Flash message if the comment doesn't exist
    
    return redirect(url_for('video'))  # Redirect back to the video page

# Error handling for role-based access and other errors
@app.errorhandler(403)
def forbidden(e):
    return render_template('error.html', message="Access forbidden: Only faculty can upload files."), 403

@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', message="Page not found!"), 404

if __name__ == '__main__':
    app.run(debug=True)
