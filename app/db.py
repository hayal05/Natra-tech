"""Neon PostgreSQL access: one connection per request, parameterized queries only."""
import psycopg2
import psycopg2.extras
from flask import current_app, g


def get_db():
    if "db" not in g:
        url = current_app.config.get("DATABASE_URL")
        if not url:
            raise RuntimeError("DATABASE_URL is not set.")
        g.db = psycopg2.connect(url, cursor_factory=psycopg2.extras.RealDictCursor)
    return g.db


def close_db(_exc=None):
    conn = g.pop("db", None)
    if conn is not None:
        conn.close()


def query(sql, args=(), one=False):
    """Run a SELECT and return rows (or a single row if one=True)."""
    with get_db().cursor() as cur:
        cur.execute(sql, args)
        return cur.fetchone() if one else cur.fetchall()


def execute(sql, args=(), returning=False):
    """Run INSERT/UPDATE/DELETE and commit. Rolls back on error.

    With returning=True the first row of a RETURNING clause is handed back."""
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, args)
            row = cur.fetchone() if returning else None
        conn.commit()
        return row
    except Exception:
        conn.rollback()
        raise


def init_app(app):
    app.teardown_appcontext(close_db)
