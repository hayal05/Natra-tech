"""Careers list and job detail pages."""
from flask import Blueprint, abort, render_template

from .. import jobs
from ..seo import job_ld

bp = Blueprint("careers", __name__, url_prefix="/careers")


@bp.route("")
def index():
    return render_template("careers.html", jobs=jobs.published_jobs())


@bp.route("/<slug>")
def detail(slug):
    job = jobs.published_job(slug) or abort(404)
    return render_template("job.html", job=job, ld=job_ld(job))
