"""Server-side Cloudinary image upload and strict YouTube ID parsing."""
import hashlib
import hmac
import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request

ALLOWED = {"image/jpeg", "image/png", "image/webp"}
MAX_IMAGE = 3 * 1024 * 1024


def upload_image(file):
    if not file or not file.filename:
        return None
    cloud = os.environ.get("CLOUDINARY_CLOUD_NAME", "").strip()
    key = os.environ.get("CLOUDINARY_API_KEY", "").strip()
    secret = os.environ.get("CLOUDINARY_API_SECRET", "").strip()
    if not all([cloud, key, secret]):
        raise ValueError("Image uploads require CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY and CLOUDINARY_API_SECRET on Render.")
    data = file.read(MAX_IMAGE + 1)
    if not data or len(data) > MAX_IMAGE:
        raise ValueError("Images must be 3 MB or smaller.")
    kind = None
    if data.startswith(b"\xff\xd8\xff"):
        kind = "image/jpeg"
    elif data.startswith(b"\x89PNG\r\n\x1a\n"):
        kind = "image/png"
    elif len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        kind = "image/webp"
    if kind not in ALLOWED:
        raise ValueError("Only real JPG, PNG and WebP images are accepted.")
    timestamp = str(int(time.time()))
    params = {"folder": "natra-website", "timestamp": timestamp}
    canonical = "&".join(f"{k}={params[k]}" for k in sorted(params))
    signature = hashlib.sha1((canonical + secret).encode()).hexdigest()
    boundary = "natra" + os.urandom(12).hex()
    parts = []
    def field(name, value):
        parts.append((f"--{boundary}\r\nContent-Disposition: form-data; name=\"{name}\"\r\n\r\n{value}\r\n").encode())
    for name, value in {**params, "api_key": key, "signature": signature}.items():
        field(name, value)
    parts.extend([
        (f"--{boundary}\r\nContent-Disposition: form-data; name=\"file\"; filename=\"upload\"\r\nContent-Type: {kind}\r\n\r\n").encode(),
        data, b"\r\n", (f"--{boundary}--\r\n").encode()
    ])
    req = urllib.request.Request(
        f"https://api.cloudinary.com/v1_1/{urllib.parse.quote(cloud, safe='')}/image/upload",
        data=b"".join(parts),
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            result = json.load(response)
    except (urllib.error.URLError, ValueError) as exc:
        raise ValueError("Image upload failed. Please retry.") from exc
    url = result.get("secure_url", "")
    if not url.startswith("https://res.cloudinary.com/"):
        raise ValueError("Image host returned an invalid URL.")
    return url


def youtube_id(value):
    value = (value or "").strip()
    if not value:
        return ""
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", value):
        return value
    parsed = urllib.parse.urlparse(value)
    host = (parsed.hostname or "").lower()
    video = ""
    if host in ("youtube.com", "www.youtube.com", "m.youtube.com") and parsed.path in ("/watch", "/"):
        video = urllib.parse.parse_qs(parsed.query).get("v", [""])[0]
    elif host in ("youtube.com", "www.youtube.com") and parsed.path.startswith(("/shorts/", "/embed/")):
        video = parsed.path.split("/")[2]
    elif host == "youtu.be":
        video = parsed.path.strip("/").split("/")[0]
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", video):
        return video
    raise ValueError("Enter a valid YouTube video URL or 11-character video ID.")
