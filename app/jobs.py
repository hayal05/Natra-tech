"""Job queries used by public pages."""
import re

from .db import execute, query


def published_jobs():
    return query("SELECT * FROM jobs WHERE status = 'published' ORDER BY created_at DESC")


def published_job(slug):
    return query("SELECT * FROM jobs WHERE slug = %s AND status = 'published'", (slug,), one=True)


EMPLOYMENT_TYPES = ["Full Time", "Part Time", "Contract", "Internship"]
# action -> (allowed current statuses, new status)
TRANSITIONS = {
    "publish": ({"draft"}, "published"),
    "unpublish": ({"published"}, "draft"),
    "archive": ({"draft", "published"}, "archived"),
    "restore": ({"archived"}, "draft"),
}


def all_jobs():
    return query(
        "SELECT j.*, (SELECT count(*) FROM applications a WHERE a.job_id = j.id) AS applications "
        "FROM jobs j ORDER BY (j.status = 'archived'), j.created_at DESC"
    )


def get_job(job_id):
    return query("SELECT * FROM jobs WHERE id = %s", (job_id,), one=True)


def _unique_slug(title):
    base = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-") or "job"
    slug, n = base, 2
    while query("SELECT 1 FROM jobs WHERE slug = %s", (slug,), one=True):
        slug, n = f"{base}-{n}", n + 1
    return slug


def create_job(d):
    execute(
        "INSERT INTO jobs (title, slug, description, responsibilities, requirements, location, employment_type) "
        "VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (d["title"], _unique_slug(d["title"]), d["description"], d["responsibilities"],
         d["requirements"], d["location"], d["employment_type"]),
    )


def update_job(job_id, d):
    """Slug is kept stable so published links never break."""
    execute(
        "UPDATE jobs SET title=%s, description=%s, responsibilities=%s, requirements=%s, "
        "location=%s, employment_type=%s, updated_at=now() WHERE id=%s",
        (d["title"], d["description"], d["responsibilities"], d["requirements"],
         d["location"], d["employment_type"], job_id),
    )


def change_status(job, action):
    allowed, new = TRANSITIONS[action]
    if job["status"] in allowed:
        execute("UPDATE jobs SET status=%s, updated_at=now() WHERE id=%s", (new, job["id"]))
        return True
    return False


def delete_archived(job):
    """Permanent delete, only for archived jobs (removes their applications too)."""
    if job["status"] == "archived":
        execute("DELETE FROM jobs WHERE id = %s", (job["id"],))
        return True
    return False


def clean_job(form):
    d = {k: form.get(k, "").strip() for k in
         ("title", "location", "employment_type", "description", "responsibilities", "requirements")}
    errors = {}
    if not 2 <= len(d["title"]) <= 150:
        errors["title"] = "Title must be 2-150 characters."
    if len(d["location"]) > 100:
        errors["location"] = "Location is too long."
    if d["employment_type"] not in EMPLOYMENT_TYPES:
        errors["employment_type"] = "Choose a valid employment type."
    for k in ("description", "responsibilities", "requirements"):
        if len(d[k]) > 5000:
            errors[k] = "Too long (max 5,000 characters)."
    return d, errors
