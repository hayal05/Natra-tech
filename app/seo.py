"""SEO helpers: site URL and JobPosting structured data."""
from flask import request

from .config import Config
from .content import COMPANY

_EMPLOYMENT = {"Full Time": "FULL_TIME", "Part Time": "PART_TIME", "Contract": "CONTRACTOR", "Internship": "INTERN"}


def site_url():
    return (Config.SITE_URL or request.url_root).rstrip("/")


def job_ld(job):
    ld = {
        "@context": "https://schema.org", "@type": "JobPosting", "title": job["title"],
        "description": job["description"] or job["title"],
        "datePosted": job["created_at"].date().isoformat(),
        "employmentType": _EMPLOYMENT.get(job["employment_type"], "OTHER"),
        "hiringOrganization": {"@type": "Organization", "name": COMPANY["name"], "sameAs": site_url()},
        "url": f"{site_url()}/careers/{job['slug']}",
    }
    place = (job["location"] or "").strip()
    if place.lower() == "remote":
        ld["jobLocationType"] = "TELECOMMUTE"
    elif place:
        ld["jobLocation"] = {"@type": "Place", "address": {"@type": "PostalAddress", "addressLocality": place}}
    return ld
