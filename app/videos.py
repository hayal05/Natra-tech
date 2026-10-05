"""Homepage video: YouTube link parsing, thumbnails and queries."""
import re
from urllib.parse import parse_qs, urlparse

import psycopg2
from flask import current_app, g, url_for

from .db import execute, query

YT_ID = re.compile(r"^[A-Za-z0-9_-]{11}$")
YT_HOSTS = {"youtube.com", "www.youtube.com", "m.youtube.com", "music.youtube.com",
            "youtube-nocookie.com", "www.youtube-nocookie.com"}
MAX_THUMB = 1_000_000  # bytes
_LIST_COLS = ("id, title, youtube_id, description, is_featured, created_at, updated_at, "
              "(thumb_data IS NOT NULL) AS has_thumb")


def parse_youtube_id(text):
    """Return the 11-character video ID from a YouTube link (or a bare ID), else None.

    Only the ID is ever stored, so nothing from the pasted link reaches the page."""
    text = (text or "").strip()
    if YT_ID.match(text):
        return text
    try:
        url = urlparse(text if "://" in text else "https://" + text)
        host, parts = (url.hostname or "").lower(), [p for p in url.path.split("/") if p]
    except ValueError:
        return None
    candidate = None
    if host == "youtu.be" and parts:
        candidate = parts[0]
    elif host in YT_HOSTS:
        if parts and parts[0] == "watch":
            candidate = (parse_qs(url.query).get("v") or [None])[0]
        elif len(parts) >= 2 and parts[0] in ("embed", "shorts", "live", "v"):
            candidate = parts[1]
    return candidate if candidate and YT_ID.match(candidate) else None


def thumbnail(v):
    """(src, fallback_src) for a video row. Custom upload wins; otherwise YouTube's own image."""
    if v["has_thumb"]:
        return url_for("main.video_thumb", video_id=v["id"], v=int(v["updated_at"].timestamp())), ""
    base = f"https://i.ytimg.com/vi/{v['youtube_id']}"
    return f"{base}/maxresdefault.jpg", f"{base}/hqdefault.jpg"  # not every video has a max-res image


def featured_video():
    """The video shown on the homepage, or None. Never raises: the homepage must load without it."""
    try:
        return query(f"SELECT {_LIST_COLS} FROM videos WHERE is_featured LIMIT 1", one=True)
    except (psycopg2.Error, RuntimeError):
        current_app.logger.exception("Could not load the featured video")
        conn = g.get("db")
        if conn is not None and not conn.closed:
            conn.rollback()
        return None


def all_videos():
    return query(f"SELECT {_LIST_COLS} FROM videos ORDER BY is_featured DESC, created_at DESC")


def get_video(video_id):
    return query(f"SELECT {_LIST_COLS} FROM videos WHERE id = %s", (video_id,), one=True)


def get_thumb(video_id):
    return query("SELECT thumb_data, thumb_type FROM videos WHERE id = %s AND thumb_data IS NOT NULL",
                 (video_id,), one=True)


def _sniff_image(data):
    """Identify the image by its first bytes rather than trusting the filename."""
    if data.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "image/webp"
    return None


def clean_video(form, files):
    """Return (values, errors). values['thumb'] is 'keep', 'remove' or 'replace'."""
    d = {
        "title": " ".join(form.get("title", "").split()),
        "url": form.get("url", "").strip(),
        "description": form.get("description", "").strip(),
        "featured": bool(form.get("featured")),
        "thumb": "remove" if form.get("remove_thumb") else "keep",
        "thumb_data": None, "thumb_type": None,
    }
    errors = {}
    if not 2 <= len(d["title"]) <= 150:
        errors["title"] = "Title must be 2-150 characters."
    d["youtube_id"] = parse_youtube_id(d["url"])
    if not d["youtube_id"]:
        errors["url"] = "Paste a YouTube video link, e.g. https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    if len(d["description"]) > 300:
        errors["description"] = "Keep the description under 300 characters."

    upload = files.get("thumbnail")
    if upload and upload.filename:
        data = upload.read(MAX_THUMB + 1)
        kind = _sniff_image(data)
        if len(data) > MAX_THUMB:
            errors["thumbnail"] = "Thumbnail is too large (max 1 MB)."
        elif not kind:
            errors["thumbnail"] = "Use a JPG, PNG or WebP image."
        else:
            d.update(thumb="replace", thumb_data=data, thumb_type=kind)
    return d, errors


def save_video(video_id, d):
    """Insert (video_id None) or update. Featuring one video un-features all others, atomically."""
    thumb_sql = {"keep": "", "remove": ", thumb_data = NULL, thumb_type = NULL",
                 "replace": ", thumb_data = %s, thumb_type = %s"}[d["thumb"]]
    thumb_args = (psycopg2.Binary(d["thumb_data"]), d["thumb_type"]) if d["thumb"] == "replace" else ()
    unfeature = "UPDATE videos SET is_featured = false WHERE is_featured; " if d["featured"] else ""
    if video_id is None:
        cols = "title, youtube_id, description, is_featured" + (", thumb_data, thumb_type" if thumb_args else "")
        marks = "%s, %s, %s, %s" + (", %s, %s" if thumb_args else "")
        execute(f"{unfeature}INSERT INTO videos ({cols}) VALUES ({marks})",
                (d["title"], d["youtube_id"], d["description"] or None, d["featured"]) + thumb_args)
    else:
        execute(f"{unfeature}UPDATE videos SET title = %s, youtube_id = %s, description = %s, "
                f"is_featured = %s, updated_at = now(){thumb_sql} WHERE id = %s",
                (d["title"], d["youtube_id"], d["description"] or None, d["featured"]) + thumb_args + (video_id,))


def set_featured(video_id, on):
    unfeature = "UPDATE videos SET is_featured = false WHERE is_featured; " if on else ""
    execute(f"{unfeature}UPDATE videos SET is_featured = %s, updated_at = now() WHERE id = %s", (on, video_id))


def delete_video(video_id):
    execute("DELETE FROM videos WHERE id = %s", (video_id,))
