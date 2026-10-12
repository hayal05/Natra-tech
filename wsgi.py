"""Entry point for Gunicorn (Render) and local runs.

Apply idempotent schema creation at startup so fresh Neon databases have
all required tables (including videos) before handling requests.
"""
from scripts.init_db import main as initialize_database
from app import create_app

initialize_database()
app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
