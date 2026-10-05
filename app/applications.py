"""Application queries."""
import re

from .db import execute, query

STATUSES = ["New", "Contacted", "Interview", "Hired", "Rejected"]
PER_PAGE = 20


def create_application(job_id, full_name, phone):
    execute(
        "INSERT INTO applications (job_id, full_name, phone, consent) VALUES (%s, %s, %s, TRUE)",
        (job_id, full_name, phone),
    )


def _where(q, job_id, status):
    where, args = ["TRUE"], []
    if q:
        name_like = "%" + re.sub(r"([\\%_])", r"\\\1", q) + "%"
        digits = re.sub(r"[\s\-().]", "", q)
        if re.search(r"\d", digits):  # only search phones when the text looks like a number
            where.append("(a.full_name ILIKE %s OR a.phone LIKE %s)")
            args += [name_like, "%" + re.sub(r"([\\%_])", r"\\\1", digits) + "%"]
        else:
            where.append("a.full_name ILIKE %s")
            args.append(name_like)
    if job_id:
        where.append("a.job_id = %s")
        args.append(job_id)
    if status in STATUSES:
        where.append("a.status = %s")
        args.append(status)
    return " AND ".join(where), args


def list_applications(q="", job_id=None, status="", newest=True, page=1):
    """Return (rows, total) for the filtered list, one page at a time."""
    where, args = _where(q, job_id, status)
    total = query(f"SELECT count(*) AS n FROM applications a WHERE {where}", args, one=True)["n"]
    order = "DESC" if newest else "ASC"
    rows = query(
        "SELECT a.*, j.title AS job_title FROM applications a JOIN jobs j ON j.id = a.job_id "
        f"WHERE {where} ORDER BY a.created_at {order}, a.id {order} LIMIT %s OFFSET %s",
        args + [PER_PAGE, (page - 1) * PER_PAGE],
    )
    return rows, total


def recent(limit=5):
    return query(
        "SELECT a.*, j.title AS job_title FROM applications a JOIN jobs j ON j.id = a.job_id "
        "ORDER BY a.created_at DESC, a.id DESC LIMIT %s", (limit,))


def stats():
    return query(
        "SELECT (SELECT count(*) FROM jobs WHERE status = 'published') AS active_jobs, "
        "(SELECT count(*) FROM applications) AS total, "
        "(SELECT count(*) FROM applications WHERE status = 'New') AS new", one=True)


def set_status(app_id, status):
    if status in STATUSES:
        execute("UPDATE applications SET status = %s, updated_at = now() WHERE id = %s", (status, app_id))
        return True
    return False
