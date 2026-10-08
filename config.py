"""App configuration, read from environment variables (or a local .env file).

Never commit real credentials. Copy .env.example to .env and fill it in.
"""
import os
import secrets

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:  # python-dotenv is optional; plain env vars still work
    pass

MONGODB_URI = os.environ.get("MONGODB_URI", "mongodb://localhost:27017")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")

# A random key keeps local dev working, but sessions reset on every restart.
# Always set SECRET_KEY in production.
SECRET_KEY = os.environ.get("SECRET_KEY") or secrets.token_hex(32)

DEBUG = os.environ.get("FLASK_DEBUG", "0") == "1"

# Max upload size in megabytes
MAX_UPLOAD_MB = int(os.environ.get("MAX_UPLOAD_MB", "50"))
