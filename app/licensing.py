"""Private manual-payment license requests and Ed25519-signed offline keys."""
import base64
import hashlib
import json
import os
import re
import secrets
from datetime import datetime, timezone

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from . import db

MAX_PROOF = 2 * 1024 * 1024
HARDWARE_PATTERN = re.compile(r"^[A-Za-z0-9:._-]{8,180}$")
PRODUCT_PATTERN = re.compile(r"^[A-Za-z0-9._-]{2,60}$")
KINDS = {"image/jpeg", "image/png", "image/webp"}


def ensure_table():
    db.execute("""CREATE TABLE IF NOT EXISTS license_requests (
       id BIGSERIAL PRIMARY KEY,
       customer_name VARCHAR(120) NOT NULL,
       customer_email VARCHAR(254) NOT NULL,
       product_code VARCHAR(60) NOT NULL,
       hardware_id VARCHAR(180) NOT NULL,
       payment_note VARCHAR(150),
       proof_data BYTEA NOT NULL,
       proof_mime VARCHAR(30) NOT NULL,
       access_hash CHAR(64) NOT NULL UNIQUE,
       status VARCHAR(16) NOT NULL DEFAULT 'pending'
         CHECK (status IN ('pending','approved','rejected')),
       license_key TEXT,
       admin_note VARCHAR(500),
       approved_by INTEGER REFERENCES admins(id) ON DELETE SET NULL,
       created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
       reviewed_at TIMESTAMPTZ
    )""")
    db.execute("CREATE INDEX IF NOT EXISTS idx_license_requests_status ON license_requests(status, created_at DESC)")


def _mime(blob):
    if blob.startswith(b"\xff\xd8\xff"):
        return "image/jpeg"
    if blob.startswith(b"\x89PNG\r\n\x1a\n"):
        return "image/png"
    if len(blob) > 12 and blob[:4] == b"RIFF" and blob[8:12] == b"WEBP":
        return "image/webp"
    return None


def clean_submission(form, files):
    name = form.get("customer_name", "").strip()
    email = form.get("customer_email", "").strip()
    product = form.get("product_code", "").strip()
    hardware = form.get("hardware_id", "").strip()
    note = form.get("payment_note", "").strip()
    proof = files.get("payment_proof")
    if not 2 <= len(name) <= 120:
        raise ValueError("Please enter your full name (2–120 characters).")
    if not 5 <= len(email) <= 254 or not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        raise ValueError("Enter a valid email address.")
    if not PRODUCT_PATTERN.fullmatch(product):
        raise ValueError("Enter a valid product code.")
    if not HARDWARE_PATTERN.fullmatch(hardware):
        raise ValueError("Hardware ID must be 8–180 letters, digits, dots, dashes, underscores or colons.")
    if len(note) > 150:
        raise ValueError("Payment reference is too long.")
    if not proof or not proof.filename:
        raise ValueError("Upload your payment screenshot.")
    blob = proof.read(MAX_PROOF + 1)
    if not blob or len(blob) > MAX_PROOF:
        raise ValueError("Payment screenshot must be 2 MB or less.")
    mime = _mime(blob)
    if mime not in KINDS:
        raise ValueError("Upload a JPG, PNG or WebP screenshot.")
    return name, email, product, hardware, note, blob, mime


def create_request(values):
    ensure_table()
    token = secrets.token_urlsafe(32)
    access_hash = hashlib.sha256(token.encode()).hexdigest()
    db.execute("""INSERT INTO license_requests (
       customer_name,customer_email,product_code,hardware_id,payment_note,
       proof_data,proof_mime,access_hash
    ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)""", (*values, access_hash))
    return token


def customer_request(token):
    if not token or len(token) > 128:
        return None
    ensure_table()
    digest = hashlib.sha256(token.encode()).hexdigest()
    return db.query("""SELECT id, product_code, hardware_id, status, license_key, admin_note, created_at
        FROM license_requests WHERE access_hash = %s""", (digest,), one=True)


def list_requests(status):
    ensure_table()
    if status not in ("pending", "approved", "rejected"):
        status = "pending"
    return db.query("""SELECT id, customer_name, customer_email, product_code, hardware_id,
        payment_note, status, created_at, reviewed_at FROM license_requests
        WHERE status = %s ORDER BY created_at DESC LIMIT 200""", (status,))


def admin_request(request_id):
    ensure_table()
    return db.query("""SELECT id, customer_name, customer_email, product_code,
        hardware_id, payment_note, proof_mime, status, license_key, admin_note, created_at
        FROM license_requests WHERE id=%s""", (request_id,), one=True)


def get_proof(request_id):
    ensure_table()
    return db.query("SELECT proof_data, proof_mime FROM license_requests WHERE id=%s",
                    (request_id,), one=True)


def _b64(data):
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def sign_license(product, hardware, request_id):
    """Keep private Ed25519 seed ONLY in Render secrets; desktop embeds public key."""
    encoded = os.environ.get("NATRA_LICENSE_PRIVATE_KEY", "").strip()
    if not encoded:
        raise ValueError("License signing is not configured yet.")
    try:
        seed = base64.urlsafe_b64decode(encoded + "=" * (-len(encoded) % 4))
        if len(seed) != 32:
            raise ValueError()
        private = Ed25519PrivateKey.from_private_bytes(seed)
    except (ValueError, TypeError) as exc:
        raise ValueError("Signing key configuration is invalid.") from exc
    payload = {"v": 1, "product": product, "hardware": hardware, "request": request_id,
               "issued": datetime.now(timezone.utc).strftime("%Y-%m-%d")}
    encoded_payload = _b64(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode())
    signature = _b64(private.sign(encoded_payload.encode("ascii")))
    return "NATRA1." + encoded_payload + "." + signature


def review(request_id, action, admin_id, note):
    if action not in ("approve", "reject") or len(note) > 500:
        raise ValueError("Invalid review action or note.")
    record = admin_request(request_id)
    if not record:
        raise ValueError("Request does not exist.")
    if record["status"] != "pending":
        raise ValueError("This request was already reviewed.")
    license_key = sign_license(record["product_code"], record["hardware_id"], request_id) if action == "approve" else None
    updated = db.execute("""UPDATE license_requests SET status=%s, license_key=%s,
        approved_by=%s, admin_note=%s, reviewed_at=now()
        WHERE id=%s AND status='pending' RETURNING id""",
        ("approved" if action == "approve" else "rejected", license_key, admin_id, note, request_id),
        returning=True)
    if not updated:
        raise ValueError("Request was already reviewed.")
