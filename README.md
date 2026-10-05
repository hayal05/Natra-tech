# Black & Gold Tech Company Website

Flask + Jinja + CSS + vanilla JS, with Neon PostgreSQL for data, Render for hosting and UptimeRobot for uptime monitoring.

**What's included:** public pages (Home, About, Services, Projects, Contact), a careers section with job pages and an application form, and an admin area at `/admin` for managing jobs, applications and the homepage video.

---

## 1. Run it locally (optional but recommended first)

```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env              # then edit .env (see section 2)
python scripts/init_db.py --seed  # creates tables + 3 sample jobs
python scripts/create_admin.py    # creates your admin login
python wsgi.py                    # http://127.0.0.1:5000
```

Leave `FLASK_ENV=development` in your local `.env`. In production it must not be set to `development` (see section 4).

---

## 2. Environment variables

Never commit real values. `.env` is already in `.gitignore`.

| Variable | Required | Purpose |
|----------|----------|---------|
| `SECRET_KEY` | Yes | Signs sessions and CSRF tokens. Use a long random string. The app refuses to start in production without it |
| `DATABASE_URL` | Yes | Neon connection string (must keep `sslmode=require`) |
| `SITE_URL` | Recommended | Your public address, e.g. `https://yourcompany.com`. Used for canonical links, sitemap and social previews |
| `FLASK_ENV` | Local only | `development` locally. Leave unset on Render (defaults to `production`) |
| `ADMIN_USERNAME` | For script | Used by `scripts/create_admin.py` |
| `ADMIN_PASSWORD` | For script | Used by `scripts/create_admin.py`. 10+ characters |

Generate a secret key:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## 3. Neon database

1. Sign up at [neon.tech](https://neon.tech) and create a **new project** (pick the region closest to your Render region and your users).
2. On the project dashboard, open **Connect** and copy the **connection string**. It looks like:
   `postgresql://user:password@ep-xxxx.neon.tech/dbname?sslmode=require`
3. Keep `?sslmode=require` at the end. Use the pooled or direct string, either works for this app.
4. Put it in your local `.env` as `DATABASE_URL`, then create the tables:

   ```bash
   python scripts/init_db.py          # tables only
   python scripts/init_db.py --seed   # tables + 3 sample jobs (optional)
   ```

   The schema is safe to run more than once. Skip `--seed` for a real launch and create your own jobs in the admin panel.
5. Create the first admin (set `ADMIN_USERNAME` and `ADMIN_PASSWORD` in `.env` first):

   ```bash
   python scripts/create_admin.py
   ```

   Running it again with the same username **resets that admin's password**.

You run these scripts from your own computer against the Neon database, so nothing needs to be run on Render itself.

---

## 4. Deploy to Render

1. Push this project to a GitHub (or GitLab) repository. Confirm `.env` is **not** in it.
2. In [Render](https://render.com), choose **New + > Web Service** and connect the repository.
3. Use these settings:

   | Setting | Value |
   |---------|-------|
   | Runtime | Python 3 |
   | Build command | `pip install -r requirements.txt` |
   | Start command | `gunicorn wsgi:app` (matches the `Procfile`) |
   | Health check path | `/health` |

4. Under **Environment**, add:
   - `SECRET_KEY` = your generated key
   - `DATABASE_URL` = your Neon string
   - `SITE_URL` = your public address (use the `https://your-app.onrender.com` address first, update it when you add a custom domain)
   - Do **not** add `FLASK_ENV`, so the app runs in production mode (secure cookies, HSTS, proxy headers).
5. Click **Create Web Service**. When the build finishes, open the `onrender.com` address.
6. The repo includes a `.python-version` file (3.12). Keep it: Render's default Python is newer, and pinning avoids package build failures. To override, set a `PYTHON_VERSION` environment variable (it takes precedence).

### Custom domain

In the service's **Settings > Custom Domains**, add your domain and create the DNS record Render shows you. Render issues the HTTPS certificate automatically. Afterwards, update `SITE_URL` to the final address so canonical links, `sitemap.xml` and social previews are correct.

### Updating the site

Push to your main branch. Render rebuilds and redeploys automatically (if auto-deploy is on). Changing the database structure later means editing `database/schema.sql` and re-running `init_db.py`; existing tables are not altered by `CREATE TABLE IF NOT EXISTS`, so plan any column changes as separate SQL.

---

## 5. UptimeRobot monitoring

1. Create a free account at [uptimerobot.com](https://uptimerobot.com).
2. Click **Add New Monitor** and set:
   - Monitor type: **HTTP(s)**
   - Friendly name: your company name
   - URL: `https://YOUR-DOMAIN.com/health`
   - Monitoring interval: 5 minutes
3. Add your email (or another alert contact) so you are notified when the site goes down.

`/health` returns `{"status":"ok"}` and exposes nothing sensitive. It does not query the database, so it confirms the web app is running, not that Neon is reachable. To also watch the database, add a second monitor on `/careers`, which reads from it.

**Free-tier note:** Render's free web services spin down after a period of inactivity, so the first visit after a quiet spell can take a while. Regular UptimeRobot pings generally keep the service awake, but check Render's current free-tier terms, as they can change.

---

## 6. After going live: checklist

- [ ] Open the site and click through every page on desktop and mobile
- [ ] Log in at `/admin`, create a test job, publish it, then apply to it from the public page
- [ ] Confirm the application appears under **Applications** and a status change saves
- [ ] Visit `/robots.txt` and `/sitemap.xml` and confirm they show your real domain
- [ ] Check the browser console for blocked resources (the Content-Security-Policy could not be verified visually during development)
- [ ] Replace placeholder content in `app/content.py` (company name, phone, email, projects)
- [ ] Delete any sample jobs you seeded

---

## Homepage video (YouTube)

Manage it in **Admin → Videos**:

1. **Add video**, paste any YouTube link (watch, `youtu.be` or Shorts), give it a title and an optional short description.
2. Thumbnail: leave the upload empty to use YouTube's own thumbnail, or upload a JPG/PNG/WebP (max 1 MB, 16:9 such as 1280×720). Custom thumbnails are stored in the database, so they survive Render redeploys.
3. Tick **Show on homepage**. Only one video is shown at a time; featuring another replaces it. **Remove from homepage** hides the section entirely.

The video loads from `youtube-nocookie.com` only after a visitor clicks play, so YouTube sets nothing until then. **If you are upgrading an existing site, run `python scripts/init_db.py` once** to create the new `videos` table (existing data is untouched).

---

## 7. Troubleshooting

| Symptom | Likely cause and fix |
|---------|----------------------|
| Deploy fails at start: `Set these environment variables in production` | Add the variables it names (`SECRET_KEY`, `DATABASE_URL`) in Render's Environment tab |
| Build fails on `psycopg2` (`pg_config executable not found`, or a compile error) | Render is using a Python version your pinned `psycopg2-binary` has no prebuilt package for. Keep `.python-version` and `psycopg2-binary==2.9.11` in `requirements.txt` |
| Connection errors (`could not connect`, SSL errors) | Check the variable name and that the string ends in `?sslmode=require` |
| Cannot log in to the admin panel | Re-run `python scripts/create_admin.py` to reset the password. After 5 failed attempts the login is temporarily locked; wait 15 minutes |
| Admin login works locally but not on Render | Production cookies are HTTPS-only. Use the `https://` address |
| Video section missing on the homepage | No video is marked **On homepage** in Admin → Videos, or `init_db.py` hasn't been run since the video feature was added |
| Forms show "400 Bad Request" | Session expired or cookies blocked. Reload the page and retry |
| Canonical links or sitemap show the wrong address | Set `SITE_URL` in Render and redeploy |
| First page load is slow | Free-tier spin-down, see section 5 |

---

## Project layout

```
app/            Flask code (routes, auth, jobs, applications, videos, SEO, security)
templates/      Jinja templates (public, admin, partials)
static/         CSS, JS, images
database/       schema.sql, seed.sql
scripts/        init_db.py, create_admin.py
Procfile        Render/gunicorn start command
.python-version  Python version Render should use
wsgi.py         Entry point
```
