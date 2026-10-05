"""Server-side validation and sanitizing for the application form."""
import re

_CONTROL = re.compile(r"[\x00-\x1f\x7f]")
_PHONE = re.compile(r"^\+?\d{7,15}$")


def clean_application(form):
    """Return (clean_values, errors). Phone is normalized (spaces, dashes, brackets removed)."""
    name = re.sub(r"\s+", " ", _CONTROL.sub("", form.get("full_name", ""))).strip()
    phone = re.sub(r"[\s\-().]", "", form.get("phone", ""))
    errors = {}
    if not 2 <= len(name) <= 100:
        errors["full_name"] = "Please enter your full name."
    if not _PHONE.match(phone):
        errors["phone"] = "Please enter a valid phone number, e.g. +251 911 000 000."
    if not form.get("consent"):
        errors["consent"] = "Please agree to be contacted to continue."
    return {"full_name": name, "phone": phone}, errors
