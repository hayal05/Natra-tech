"""Create or reset an admin account using ADMIN_USERNAME and ADMIN_PASSWORD.

Usage: python scripts/create_admin.py
Running it again with the same username resets that admin's password.
"""
import os
import pathlib
import sys

import psycopg2
from werkzeug.security import generate_password_hash

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from app.config import Config  # noqa: E402


def main():
    username = os.environ.get("ADMIN_USERNAME", "").strip()
    password = os.environ.get("ADMIN_PASSWORD", "")
    if not Config.DATABASE_URL or not username:
        sys.exit("Set DATABASE_URL and ADMIN_USERNAME first.")
    if len(password) < 10:
        sys.exit("ADMIN_PASSWORD must be at least 10 characters.")
    with psycopg2.connect(Config.DATABASE_URL) as conn, conn.cursor() as cur:
        cur.execute(
            "INSERT INTO admins (username, password_hash) VALUES (%s, %s) "
            "ON CONFLICT (username) DO UPDATE SET password_hash = EXCLUDED.password_hash",
            (username, generate_password_hash(password)),
        )
    print(f"Admin '{username}' is ready.")


if __name__ == "__main__":
    main()
