# Offline software license portal

## Customer
- Open /license/request, provide name, email, software product code, hardware ID and payment screenshot (JPG/PNG/WebP, <=2 MB).
- The portal creates a private unguessable status link. **Copy/save the link immediately**; it is not emailed.
- Approval is always manual. Payment screenshots are merely evidence; **admin must independently verify actual payment** before approving.

## Admin
- Sign in and use Admin > Licenses. Inspect each proof by opening a request.
- Approve or reject using the protected form. Once reviewed, the request cannot be reviewed a second time.
- Approval requires a signing key. If unset, the admin receives a configuration error and nothing is issued.
- For refunds/transfers/replacements/revocation, add separate flows before selling large quantities. A fully offline app cannot be remotely revoked while offline.

## One-time setup
1. Run `python scripts/generate_license_keys.py` on your trusted local computer.
2. Copy `NATRA_LICENSE_PRIVATE_KEY` into **Render secret environment settings** and redeploy; never commit it or show it to customers.
3. Embed `OFFLINE_APP_PUBLIC_KEY` in the offline software's license verifier (NOT the signing seed).
4. Apply database/schema.sql using scripts/init_db.py or ensure the DB role can create the table at first use.

## Key protocol (NATRA1)
The portal issues `NATRA1.<base64url-canonical-JSON>.<base64url-Ed25519-signature>`.
Signature is over ASCII `<base64url-canonical-JSON>`, *not* over decoded JSON and not including `NATRA1.`.
Payload fields: `v` integer 1, `product`, `hardware`, `request`, `issued` ISO UTC date.
The offline app must:
1. Parse exact three dot-separated segments, version NATRA1; reject malformed entries.
2. Verify the Ed25519 signature over the middle ASCII segment using the embedded public key.
3. Parse JSON only after signature verification; validate version, product identifier and current normalized hardware ID match EXACTLY.
4. Cache/store the validated key locally, securely as practical. Reject failed checks.
Do NOT hardcode the private key into offline software. An approved key is not a working license until client verification is implemented.

## Operational precautions
- DB payment screenshots are private BYTEA, served only after admin login (not public/static/Cloudinary).
- Access to customer license keys uses a long secret status URL; anybody who gets that URL can view the license.
- Key issuing requires both admin login and explicit manual approval.
- Never treat upload proof alone as confirmed payment.
- The present MVP has no email delivery, billing integration, audit log, usage reporting, public submission throttling, or automated fraud verification. Before exposing at scale, add reverse-proxy request limiting and abuse monitoring.
