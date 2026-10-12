"""Gunicorn/Render entry point with optional one-time admin provisioning.

Set INIT_ADMIN_ON_STARTUP=true temporarily to create/reset the account
using ADMIN_USERNAME and ADMIN_PASSWORD stored in Render Environment.
Remove the toggle and password after successful deployment.
"""
import os

from scripts.init_db import main as initialize_database
from app import create_app

initialize_database()

if os.environ.get("INIT_ADMIN_ON_STARTUP", "").lower() == "true":
    from scripts.create_admin import main as initialize_admin

    initialize_admin()

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
