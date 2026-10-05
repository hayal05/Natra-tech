"""Apply database/schema.sql to the database in DATABASE_URL.

Usage: python scripts/init_db.py [--seed]
"""
import pathlib
import sys

import psycopg2

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from app.config import Config  # noqa: E402


def main():
    if not Config.DATABASE_URL:
        sys.exit("DATABASE_URL is not set.")
    schema = pathlib.Path(__file__).resolve().parent.parent / "database" / "schema.sql"
    files = [schema] + ([schema.with_name("seed.sql")] if "--seed" in sys.argv else [])
    with psycopg2.connect(Config.DATABASE_URL) as conn, conn.cursor() as cur:
        for f in files:
            cur.execute(f.read_text())
    print("Schema applied" + (" with sample jobs." if "--seed" in sys.argv else "."))


if __name__ == "__main__":
    main()
