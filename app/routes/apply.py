"""Job application form."""
from flask import Blueprint, abort, current_app, redirect, render_template, request, url_for

from .. import jobs
from ..applications import create_application
from ..validation import clean_application

bp = Blueprint("apply", __name__, url_prefix="/apply")


def _job_or_404(slug):
    return jobs.published_job(slug) or abort(404)


@bp.route("/<slug>", methods=["GET", "POST"])
def form(slug):
    job = _job_or_404(slug)
    if request.method == "GET":
        return render_template("apply.html", job=job)

    # Honeypot: real users never fill this hidden field; pretend success to bots.
    if request.form.get("website"):
        return redirect(url_for("apply.received", slug=slug))

    values, errors = clean_application(request.form)
    if errors:
        return render_template("apply.html", job=job, values=values, errors=errors), 400
    try:
        create_application(job["id"], values["full_name"], values["phone"])
    except Exception:
        current_app.logger.exception("Failed to save application")
        return render_template("apply.html", job=job, values=values, errors={},
                               failure=True), 503
    return redirect(url_for("apply.received", slug=slug))


@bp.route("/<slug>/received")
def received(slug):
    return render_template("apply_received.html", job=_job_or_404(slug))
