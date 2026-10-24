"""Editable public site content backed by Neon; current copy is the initial default."""
import copy
import json
from flask import current_app
from . import db
from .content import PROJECTS, SERVICES, STATS, VALUES

DEFAULTS = {
    "hero_label": "Technology studio",
    "hero_title": "We build what's",
    "hero_accent": "next.",
    "hero_description": "Digital products, software and intelligent systems for modern businesses.",
    "about_title": "Built to",
    "about_accent": "last.",
    "about_description": "A technology company focused on building useful, scalable and memorable digital products.",
    "mission_title": "Make technology useful.",
    "mission_description": "We turn complex problems into simple, dependable products that people actually enjoy using.",
    "vision_title": "Set the standard.",
    "vision_description": "To be the studio businesses trust when quality, speed and craft all matter.",
    "cta_title": "Have something in",
    "cta_accent": "mind?",
    "stats": [{"value": value, "label": label} for value, label in STATS],
    "projects": copy.deepcopy(PROJECTS),
    "services": [{"title": title, "tagline": tagline, "detail": detail} for _, title, tagline, detail in SERVICES],
    "values": [{"title": title, "description": description} for title, description in VALUES],
}

FIELDS = {k: 400 for k in DEFAULTS if isinstance(DEFAULTS[k], str)}
FIELDS.update({"hero_description": 1000, "about_description": 1000, "mission_description": 1000, "vision_description": 1000})
COLLECTIONS = {
    "stats": {"value": 40, "label": 100},
    "projects": {"name": 120, "tags": 180, "year": 12, "variant": 1},
    "services": {"title": 120, "tagline": 240, "detail": 1000},
    "values": {"title": 100, "description": 600},
}
LIMITS = {"stats": 6, "projects": 30, "services": 12, "values": 9}
VARIANTS = ("a", "b", "c")


def _table():
    db.execute("""CREATE TABLE IF NOT EXISTS site_content (
        id SMALLINT PRIMARY KEY CHECK (id = 1),
        content JSONB NOT NULL,
        updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
    )""")


def get_content():
    data = copy.deepcopy(DEFAULTS)
    try:
        _table()
        row = db.query("SELECT content FROM site_content WHERE id = 1", one=True)
        if row:
            saved = row["content"]
            if isinstance(saved, str):
                saved = json.loads(saved)
            for key in DEFAULTS:
                if key in saved and isinstance(saved[key], type(DEFAULTS[key])):
                    data[key] = saved[key]
    except Exception:
        current_app.logger.exception("Could not load site content; serving defaults")
    return data


def from_form(form):
    """Whitelist fields and enforce bounded, plain-text content."""
    data, errors = {}, []
    for key, max_length in FIELDS.items():
        value = form.get(key, "").strip()
        if not value or len(value) > max_length:
            errors.append(f"{key.replace('_', ' ').title()} must be 1–{max_length} characters.")
        data[key] = value
    for group, fields in COLLECTIONS.items():
        try:
            count = int(form.get(f"{group}_count", "-1"))
        except ValueError:
            count = -1
        if count < 0 or count > LIMITS[group]:
            errors.append(f"Invalid number of {group}.")
            count = 0
        rows = []
        for i in range(count):
            row = {}
            for key, max_length in fields.items():
                value = form.get(f"{group}_{i}_{key}", "").strip()
                if group == "projects" and key == "variant":
                    if value not in VARIANTS:
                        errors.append(f"Project {i + 1}: invalid style.")
                elif not value or len(value) > max_length:
                    errors.append(f"{group.title()} row {i + 1}: {key} must be 1–{max_length} characters.")
                row[key] = value
            rows.append(row)
        data[group] = rows
    return data, errors


def save_content(data):
    _table()
    db.execute("""INSERT INTO site_content (id, content) VALUES (1, %s::jsonb)
        ON CONFLICT (id) DO UPDATE SET content = EXCLUDED.content, updated_at = now()""",
        (json.dumps(data),))
