"""Public routes."""
from flask import Blueprint, Response, abort, jsonify, render_template

from .. import videos
from ..content import PROJECTS, SERVICES, STATS, VALUES

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    return render_template("index.html", services=SERVICES, projects=PROJECTS, stats=STATS,
                           video=videos.featured_video())


@bp.route("/video-thumb/<int:video_id>")
def video_thumb(video_id):
    """Serves an admin-uploaded thumbnail. URLs carry a version, so browsers may cache them for long."""
    row = videos.get_thumb(video_id) or abort(404)
    return Response(bytes(row["thumb_data"]), mimetype=row["thumb_type"],
                    headers={"Cache-Control": "public, max-age=31536000, immutable"})


@bp.route("/about")
def about():
    return render_template("about.html", stats=STATS, values=VALUES)


@bp.route("/services")
def services():
    return render_template("services.html", services=SERVICES)


@bp.route("/projects")
def projects():
    return render_template("projects.html", projects=PROJECTS)


@bp.route("/contact")
def contact():
    return render_template("contact.html")


@bp.route("/health")
def health():
    """Uptime check for UptimeRobot. Exposes no sensitive data."""
    return jsonify(status="ok")
