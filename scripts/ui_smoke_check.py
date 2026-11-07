"""Static UI regression checks; safe without a database or production secrets.

Run: python scripts/ui_smoke_check.py
Requires: Flask/Jinja2 (pip install -r requirements.txt).
"""
from __future__ import annotations

import re
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, meta

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "templates"
STATIC = ROOT / "static"
EXPECTED_ADMIN_LINKS = (
    "/admin/dashboard", "/admin/applications", "/admin/jobs",
    "/admin/content", "/admin/licenses", "/admin/videos", "/admin/logout",
)
EXPECTED_PUBLIC_LINKS = ("/about", "/services", "/projects", "/careers", "/contact")
VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link",
             "meta", "param", "source", "track", "wbr"}


def check_html_balance(path: Path, source: str) -> None:
    # Structural check only; Jinja conditional branches are checked by template compilation.
    stack: list[str] = []
    for match in re.finditer(r"</?([a-z][\w:-]*)\b[^>]*>", source, flags=re.I | re.S):
        tag, raw = match.group(1).lower(), match.group()
        if tag in VOID_TAGS or raw.rstrip().endswith("/>"):
            continue
        if raw.startswith("</"):
            if not stack or stack[-1] != tag:
                raise AssertionError(f"{path}: unexpected </{tag}> after {stack[-1] if stack else 'nothing'}")
            stack.pop()
        else:
            stack.append(tag)
    if stack:
        raise AssertionError(f"{path}: unclosed tags: {stack}")


def main() -> None:
    env = Environment(loader=FileSystemLoader(str(TEMPLATES)), autoescape=True)
    templates = sorted(TEMPLATES.rglob("*.html"))
    assert templates, "No HTML templates found"
    for path in templates:
        name = str(path.relative_to(TEMPLATES))
        src = path.read_text(encoding="utf-8")
        ast = env.parse(src)
        for referenced in meta.find_referenced_templates(ast):
            if referenced is not None:
                assert (TEMPLATES / referenced).is_file(), f"{name}: missing {referenced}"
        check_html_balance(path, src)

    for path in templates:
        src = path.read_text(encoding="utf-8")
        for asset in re.findall(r"filename=['\"](css/[^'\"]+|js/[^'\"]+)['\"]", src):
            assert (STATIC / asset).is_file(), f"{path.name}: missing static asset {asset}"

    admin = (TEMPLATES / "admin/layout.html").read_text(encoding="utf-8")
    public = (TEMPLATES / "partials/header.html").read_text(encoding="utf-8")
    assert all(route in admin for route in EXPECTED_ADMIN_LINKS), "Admin navigation route missing"
    assert all(route in public for route in EXPECTED_PUBLIC_LINKS), "Public navigation route missing"
    assert 'name="csrf_token"' in admin and 'action="/admin/logout"' in admin
    form = (TEMPLATES / "partials/apply_form.html").read_text(encoding="utf-8")
    for field in ("csrf_token", "full_name", "phone", "consent", "website"):
        assert f'name="{field}"' in form, f"Application form missing {field}"
    assert 'action="/apply/{{ job.slug }}"' in form

    print(f"PASS: compiled {len(templates)} Jinja templates, checked local CSS/JS assets, "
          "navigation, HTML structure, and application safety fields.")


if __name__ == "__main__":
    main()
