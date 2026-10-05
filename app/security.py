"""CSRF protection for all POST requests (session-based token)."""
import secrets

from flask import abort, current_app, request, session


def csrf_token():
    if "_csrf" not in session:
        session["_csrf"] = secrets.token_hex(32)
    return session["_csrf"]


def init_csrf(app):
    app.jinja_env.globals["csrf_token"] = csrf_token

    @app.before_request
    def verify_csrf():
        if request.method == "POST":
            sent, expected = request.form.get("csrf_token", ""), session.get("_csrf", "")
            if not sent or not expected or not secrets.compare_digest(sent, expected):
                abort(400)  # a missing token must never match a missing session token


CSP = ("default-src 'self'; script-src 'self'; script-src-attr 'unsafe-inline'; "
       "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src https://fonts.gstatic.com; "
       "img-src 'self' data: https://i.ytimg.com; "
       "frame-src https://www.youtube-nocookie.com; form-action 'self'; base-uri 'self'; frame-ancestors 'none'")


def init_headers(app):
    @app.after_request
    def add_headers(response):
        response.headers.update({
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
            "Content-Security-Policy": CSP,
        })
        if current_app.config["ENV"] == "production":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response
