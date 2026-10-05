"""Admin area routes: login, jobs and applications management."""
from flask import Blueprint, abort, flash, redirect, render_template, request, session, url_for

from .. import applications as apps
from .. import auth, jobs, videos

bp = Blueprint("admin", __name__, url_prefix="/admin")


@bp.after_request
def private_headers(response):
    response.headers["Cache-Control"] = "no-store"
    response.headers["X-Robots-Tag"] = "noindex, nofollow"
    return response


@bp.route("", methods=["GET", "POST"])
def login():
    if "admin_id" in session:
        return redirect(url_for("admin.dashboard"))
    error = None
    if request.method == "POST":
        ip = request.remote_addr or "unknown"
        if auth.too_many_attempts(ip):
            return render_template("admin/login.html", error="Too many attempts. Try again later."), 429
        admin = auth.authenticate(request.form.get("username", "").strip(), request.form.get("password", ""))
        if admin:
            auth.login_user(admin)
            return redirect(url_for("admin.dashboard"))
        auth.record_failure(ip)
        error = "Invalid username or password."
        return render_template("admin/login.html", error=error), 401
    return render_template("admin/login.html", error=error)


@bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("admin.login"))


@bp.route("/dashboard")
@auth.login_required
def dashboard():
    return render_template("admin/dashboard.html", stats=apps.stats(), recent=apps.recent())


def _job_or_404(job_id):
    return jobs.get_job(job_id) or abort(404)


@bp.route("/jobs")
@auth.login_required
def jobs_list():
    return render_template("admin/jobs.html", jobs=jobs.all_jobs())


@bp.route("/jobs/new", methods=["GET", "POST"])
@bp.route("/jobs/<int:job_id>/edit", methods=["GET", "POST"])
@auth.login_required
def job_form(job_id=None):
    job = _job_or_404(job_id) if job_id else None
    values, errors = (job or {}), {}
    if request.method == "POST":
        values, errors = jobs.clean_job(request.form)
        if not errors:
            jobs.update_job(job_id, values) if job else jobs.create_job(values)
            flash("Job updated." if job else "Job created as a draft. Publish it from the list.")
            return redirect(url_for("admin.jobs_list"))
    return render_template("admin/job_form.html", job=job, values=values, errors=errors,
                           types=jobs.EMPLOYMENT_TYPES), (400 if errors else 200)


@bp.route("/jobs/<int:job_id>/<action>", methods=["POST"])
@auth.login_required
def job_action(job_id, action):
    job = _job_or_404(job_id)
    if action == "delete":
        done = jobs.delete_archived(job)
    elif action in jobs.TRANSITIONS:
        done = jobs.change_status(job, action)
    else:
        abort(404)
    flash(f"Job {action}d." if done else "That action isn't available for this job.")
    return redirect(url_for("admin.jobs_list"))


@bp.route("/applications")
@auth.login_required
def applications_list():
    a = request.args
    page = max(a.get("page", 1, type=int), 1)
    rows, total = apps.list_applications(a.get("q", "").strip()[:100], a.get("job", type=int),
                                         a.get("status", ""), a.get("sort") != "oldest", page)
    return render_template("admin/applications.html", rows=rows, total=total, page=page,
                           pages=max(-(-total // apps.PER_PAGE), 1), jobs=jobs.all_jobs(),
                           statuses=apps.STATUSES, f=a)


@bp.route("/applications/<int:app_id>/status", methods=["POST"])
@auth.login_required
def application_status(app_id):
    flash("Status updated." if apps.set_status(app_id, request.form.get("status", "")) else "Invalid status.")
    nxt = request.form.get("next", "")  # only ever return to the applications list
    return redirect(nxt if nxt.startswith("/admin/applications") else url_for("admin.applications_list"))


def _video_or_404(video_id):
    return videos.get_video(video_id) or abort(404)


@bp.route("/videos")
@auth.login_required
def videos_list():
    return render_template("admin/videos.html", videos=videos.all_videos())


@bp.route("/videos/new", methods=["GET", "POST"])
@bp.route("/videos/<int:video_id>/edit", methods=["GET", "POST"])
@auth.login_required
def video_form(video_id=None):
    video = _video_or_404(video_id) if video_id else None
    values, errors = (video or {}), {}
    if request.method == "POST":
        values, errors = videos.clean_video(request.form, request.files)
        if not errors:
            videos.save_video(video_id, values)
            flash("Video updated." if video else "Video added.")
            return redirect(url_for("admin.videos_list"))
        values = {**values, "is_featured": values["featured"], "description": values["description"]}
    return render_template("admin/video_form.html", video=video, values=values, errors=errors), (400 if errors else 200)


@bp.route("/videos/<int:video_id>/<action>", methods=["POST"])
@auth.login_required
def video_action(video_id, action):
    _video_or_404(video_id)
    if action in ("feature", "unfeature"):
        videos.set_featured(video_id, action == "feature")
        flash("Video is now on the homepage." if action == "feature" else "Video removed from the homepage.")
    elif action == "delete":
        videos.delete_video(video_id)
        flash("Video deleted.")
    else:
        abort(404)
    return redirect(url_for("admin.videos_list"))
