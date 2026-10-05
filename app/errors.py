"""Branded error pages. Messages never expose internal details."""
import psycopg2
from flask import render_template

ERRORS = {
    400: ("Bad request", "That request couldn't be processed. Please go back and try again."),
    403: ("Access denied", "You don't have permission to view this page."),
    404: ("Page not found", "The page you're looking for doesn't exist or has moved."),
    405: ("Not allowed", "That action isn't allowed here."),
    413: ("File too large", "That upload is too large. Please go back and choose a smaller file."),
    500: ("Something went wrong", "An unexpected error occurred. We've been notified. Please try again shortly."),
    503: ("Temporarily unavailable", "We're having trouble right now. Please try again in a moment."),
}


def _page(code):
    title, message = ERRORS[code]
    return render_template("error.html", code=code, title=title, message=message), code


def init_app(app):
    for code in ERRORS:
        app.register_error_handler(code, lambda _e, code=code: _page(code))
    # A database outage should look like a brief outage, not a crash.
    app.register_error_handler(psycopg2.OperationalError, lambda _e: _page(503))
