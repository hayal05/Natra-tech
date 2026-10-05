"""Admin authentication: password check, session handling, brute-force limiting."""
import time
from functools import wraps

from flask import flash, redirect, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from .db import query

_DUMMY_HASH = generate_password_hash("not-a-real-password")  # keeps timing equal for unknown users
MAX_FAILURES, WINDOW = 5, 15 * 60
_failures = {}  # ip -> [timestamps]; per worker process, resets on restart


def _recent(ip):
    now = time.time()
    _failures[ip] = [t for t in _failures.get(ip, []) if now - t < WINDOW]
    return _failures[ip]


def too_many_attempts(ip):
    return len(_recent(ip)) >= MAX_FAILURES


def record_failure(ip):
    _recent(ip).append(time.time())


def authenticate(username, password):
    admin = query("SELECT id, username, password_hash FROM admins WHERE username = %s", (username,), one=True)
    ok = check_password_hash(admin["password_hash"] if admin else _DUMMY_HASH, password)
    return admin if admin and ok else None


def login_user(admin):
    session.clear()  # new session on login prevents fixation
    session.permanent = True
    session["admin_id"], session["admin_name"] = admin["id"], admin["username"]


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "admin_id" not in session:
            flash("Please sign in to continue.")
            return redirect(url_for("admin.login"))
        return view(*args, **kwargs)
    return wrapped
