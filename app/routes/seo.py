"""robots.txt and sitemap.xml."""
from xml.sax.saxutils import escape

from flask import Blueprint, Response, current_app

from .. import jobs
from ..seo import site_url

bp = Blueprint("seo", __name__)
PAGES = ["/", "/about", "/services", "/projects", "/careers", "/contact"]


@bp.route("/robots.txt")
def robots():
    body = f"User-agent: *\nDisallow: /admin\nDisallow: /apply/\nSitemap: {site_url()}/sitemap.xml\n"
    return Response(body, mimetype="text/plain")


@bp.route("/sitemap.xml")
def sitemap():
    urls = [(p, None) for p in PAGES]
    try:
        urls += [(f"/careers/{j['slug']}", j["updated_at"].date().isoformat()) for j in jobs.published_jobs()]
    except Exception:  # keep the sitemap useful even if the database is down
        current_app.logger.exception("Sitemap: could not load jobs")
    items = "".join(
        f"<url><loc>{escape(site_url() + path)}</loc>{f'<lastmod>{last}</lastmod>' if last else ''}</url>"
        for path, last in urls)
    xml = f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{items}</urlset>'
    return Response(xml, mimetype="application/xml")
