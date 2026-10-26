"""Public license request and private receipt-token status page."""
from flask import Blueprint, abort, flash, redirect, render_template, request, url_for
from .. import licensing

bp = Blueprint("licenses", __name__, url_prefix="/license")

@bp.after_request
def private(response):
    response.headers["Cache-Control"] = "no-store"
    response.headers["X-Robots-Tag"] = "noindex, nofollow"
    return response

@bp.route("/request", methods=["GET", "POST"])
def submit():
    error = None
    if request.method == "POST":
        try:
            values = licensing.clean_submission(request.form, request.files)
            token = licensing.create_request(values)
            return redirect(url_for("licenses.status", token=token))
        except ValueError as exc:
            error = str(exc)
    return render_template("licenses/request.html", error=error), (400 if error else 200)

@bp.route("/status/<token>")
def status(token):
    row = licensing.customer_request(token)
    if not row:
        abort(404)
    return render_template("licenses/status.html", item=row, token=token)
