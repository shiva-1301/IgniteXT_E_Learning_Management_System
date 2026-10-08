# IgniteXT — E-Learning Content Management System

IgniteXT is a web-based e-learning platform where **faculty** upload study materials and lectures, and **students** browse courses, watch videos, follow developer roadmaps, download resources and get help from a built-in **AI study assistant** powered by Google Gemini.

**Live demo:** _coming soon — see [Deployment](#deployment)_

![IgniteXT screenshot](docs/screenshot.png)
<!-- Add a screenshot at docs/screenshot.png -->

---

## Features

| | |
|---|---|
| 🔐 **Authentication** | Sign up / sign in with role selection (Student or Faculty), bcrypt-hashed passwords, session-based auth |
| 🎓 **Courses & playlists** | Course catalogue, playlist pages and a video player with live search filtering |
| 💬 **Comments** | Students comment on lessons; faculty can moderate (delete) comments |
| 📁 **Study materials** | Faculty upload files (drag and drop, size limit, blocked executable types); everyone can download |
| 🗺️ **Developer roadmaps** | 25 PDF roadmaps (Frontend, Backend, DevOps, AI, Python, Java…) |
| 🤖 **AI assistant** | Chat with Google Gemini for study help, with typing indicator and suggested prompts |
| 🌗 **Light / dark mode** | Remembers your preference |
| 📱 **Responsive** | Works on mobile, tablet and desktop; keyboard and screen-reader friendly |

## Tech stack

- **Backend:** Python 3, Flask, Flask-Bcrypt
- **Database:** MongoDB (MongoDB Atlas) via PyMongo
- **AI:** Google Gemini (`google-generativeai`)
- **Frontend:** Jinja2 templates, vanilla CSS (custom design system) and vanilla JavaScript, Font Awesome, Inter font
- **Deployment:** Gunicorn on Render

## Project structure

```
├── app.py               # Flask app: routes, auth, uploads, chatbot API
├── config.py            # Reads settings from environment variables
├── requirements.txt
├── render.yaml          # One-click Render deployment blueprint
├── .env.example         # Template for local environment variables
├── static/
│   ├── css/main.css     # Design system + all page styles
│   ├── js/main.js       # Theme toggle, sidebar, menus, search
│   ├── images/          # Logos, thumbnails, avatars, demo videos
│   └── roadmaps/        # Developer roadmap PDFs
├── templates/
│   ├── base.html        # HTML skeleton
│   ├── layout.html      # App shell: header, sidebar, footer
│   ├── _macros.html     # Reusable components (flash messages, course card)
│   └── *.html           # Pages
└── uploads/             # Files uploaded by faculty (created at runtime, git-ignored)
```

## Getting started

### Prerequisites
- Python 3.10+
- A MongoDB database (free [MongoDB Atlas](https://www.mongodb.com/atlas) cluster or local MongoDB)
- A [Google Gemini API key](https://aistudio.google.com/app/apikey) (optional; only the chatbot needs it)

### Setup

```bash
git clone https://github.com/shiva-1301/IgniteXT_E_Learning_Management_System.git
cd IgniteXT_E_Learning_Management_System

python -m venv venv
# Windows: venv\Scripts\activate    macOS/Linux: source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env      # then edit .env with your own values
python app.py
```

Open http://127.0.0.1:5000. Register as **Faculty** to see the Upload page, or as **Student** for the learner view.

### Environment variables

| Variable | Required | Description |
|---|---|---|
| `MONGODB_URI` | ✅ | MongoDB connection string |
| `SECRET_KEY` | ✅ in production | Flask session signing key (`python -c "import secrets; print(secrets.token_hex(32))"`) |
| `GEMINI_API_KEY` | optional | Enables the AI assistant |
| `GEMINI_MODEL` | optional | Defaults to `gemini-2.0-flash` |
| `FLASK_DEBUG` | optional | `1` to enable debug mode locally |
| `MAX_UPLOAD_MB` | optional | Upload size limit, default `50` |

## Deployment

The repo includes a [`render.yaml`](render.yaml) blueprint for [Render](https://render.com) (free tier).

1. Push this repository to GitHub.
2. In MongoDB Atlas, go to **Network Access** and allow `0.0.0.0/0` (Render IPs are dynamic).
3. On Render, choose **New → Blueprint** and select this repo. Render reads `render.yaml`.
4. When prompted, enter `MONGODB_URI` and `GEMINI_API_KEY`. `SECRET_KEY` is generated automatically.
5. Deploy. Your app will be live at `https://ignitext.onrender.com` (or similar).

> **Note:** Render's free tier has an ephemeral filesystem, so files uploaded by faculty are lost on redeploy or restart. For persistent uploads, add a Render Disk mounted at `/opt/render/project/src/uploads`, or move uploads to cloud storage (S3, Cloudinary or MongoDB GridFS).

## Roadmap / ideas

- Store courses, playlists and videos in MongoDB so faculty can create them from the UI
- Real likes and saved playlists
- CSRF protection (Flask-WTF) and rate limiting on login
- Password reset via email

## License

Educational project. © IgniteXT.
