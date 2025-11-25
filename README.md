🎓 IgniteXT E-Learning Management System
🧠 Tech Stack
HTML | CSS | JavaScript | Flask | Python | MongoDB

📘 Overview
IgniteXT E-Learning Management System is a full-stack web application that provides an interactive learning experience for students, instructors, and administrators.
It enables course management, progress tracking, and data-driven insights — all through a clean, responsive, and secure interface.

⚙️ Key Features
🔐 Role-Based Authentication – Secure login for students, instructors, and admins with dedicated dashboards.
📚 Course Management – Instructors can upload courses, videos, and materials; students can enroll and learn at their own pace.
📈 Analytics Dashboard – Tracks course engagement, completion rates, and student performance trends.
🎥 Video Streaming Integration – Delivers smooth, high-quality educational content directly within the platform.
📱 Responsive Design – Optimized for desktop, tablet, and mobile devices.
🧭 Seamless Navigation – Clean UI with intuitive menus and course progress indicators.
🧩 System Architecture
Frontend: HTML, CSS, JavaScript
Backend: Flask (Python)
Database: MongoDB
Authentication: Flask-Login & JWT
Media Streaming: HTML5 Video Player Integration

🗺️ User Roles
👨‍🎓 Students – Access enrolled courses, watch lectures, track progress, and download resources.
👩‍🏫 Instructors – Create and manage courses, upload content, and analyze student engagement.
🧑‍💼 Admins – Oversee platform activity, manage users, and generate analytics reports.
📊 Example: Student Progress Analytics
# Flask Route Example for Student Progress Data
@app.route('/progress/<student_id>')
def progress(student_id):
    progress_data = db.progress.find_one({'student_id': student_id})
    return jsonify(progress_data)
About
No description, website, or topics provided.
Resources
 Readme
 Activity
Stars
 0 stars
Watchers
 0 watching
Forks
 0 forks
Releases
No releases published
Create a new release
Packages
No packages published
Publish your first package
Footer
