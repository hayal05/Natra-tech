"""Public routes."""
from flask import Blueprint, Response, abort, current_app, jsonify, render_template, send_from_directory

from .. import videos, site_content

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    return render_template("index.html", content=site_content.get_content(),
                           video=videos.featured_video())


@bp.route("/googleff19c7fdad59d6da.html")
def google_site_verification():
    """Serve Google Search Console ownership verification at the domain root."""
    return send_from_directory(current_app.static_folder, "googleff19c7fdad59d6da.html", mimetype="text/html")


@bp.route("/video-thumb/<int:video_id>")
def video_thumb(video_id):
    """Serves an admin-uploaded thumbnail. URLs carry a version, so browsers may cache them for long."""
    row = videos.get_thumb(video_id) or abort(404)
    return Response(bytes(row["thumb_data"]), mimetype=row["thumb_type"],
                    headers={"Cache-Control": "public, max-age=31536000, immutable"})


@bp.route("/about")
def about():
    return render_template("about.html", content=site_content.get_content())


@bp.route("/services")
def services():
    return render_template("services.html", content=site_content.get_content())


@bp.route("/projects")
def projects():
    return render_template("projects.html", content=site_content.get_content())


@bp.route("/contact")
def contact():
    return render_template("contact.html")


@bp.route("/health")
def health():
    """Uptime check for UptimeRobot. Exposes no sensitive data."""
    return jsonify(status="ok")
