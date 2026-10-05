# Project Status

**Last updated:** 2026-10-05
**Overall:** Steps 1-10 approved. Step 11 (Final QA) done. Awaiting final sign-off.
**Lines used:** 1,786 / 3,000

## Progress
| # | Task | Status | Lines | Notes |
|---|------|--------|-------|-------|
| 1 | Foundation | Approved | 183 / ~200 | App factory, config, Neon db layer, schema, init script |
| 2 | Design system & layout | Approved | 245 / ~350 | Tokens, base layout, header/footer partials, mobile menu, reveal JS. Index is a temporary preview |
| 3 | Public pages | Approved | 233 / ~500 | Home, About, Services, Projects, Contact. Content lives in `app/content.py` (placeholder text) |
| 4 | Careers | Approved | 129 / ~250 | Job list, job detail, empty state, optional sample jobs (`--seed`). Verified on a local Postgres |
| 5 | Application flow | Approved | 150 / ~200 | Form, validation, CSRF, honeypot, success + failure states. Verified on a local Postgres |
| 6 | Admin auth | Approved | 193 / ~200 | Login/logout, hashed passwords, sessions, login lockout, `scripts/create_admin.py`. Verified on a local Postgres |
| 7 | Admin jobs | Approved | 206 / ~300 | Jobs list, create/edit, publish/unpublish, archive/restore, delete (archived only). 19 end-to-end checks pass on a local Postgres |
| 8 | Admin applications | Approved | 147 / ~300 | Dashboard stats + recent, list with search/job/status filters, newest/oldest sort, pagination (20/page), inline status updates. 23 end-to-end checks pass on a local Postgres |
| 9 | Polish & SEO | Approved | 140 / ~250 | Branded 400/403/404/405/500/503 pages, canonical + Open Graph + Twitter tags, JobPosting/Organization JSON-LD, robots.txt, sitemap.xml, security headers (CSP, HSTS in production), og.png, favicon. 26 end-to-end checks pass on a local Postgres. Also fixed a CSRF bug (empty token matched empty session token) |
| 10 | Deployment docs | Approved | 155 / ~150 | `README.md`: local setup, env vars, Neon, Render, UptimeRobot, post-launch checklist, troubleshooting |
| 11 | Final QA | Awaiting review | 0 net | 104 automated checks pass (public routes, SEO, headers, apply form + validation, CSRF, admin auth + lockout, jobs workflow, applications workflow, redirects, XSS escaping) on a stubbed database. Templates compile, all internal links and assets resolve, mobile CSS reviewed. Fixes: `COMPANY` now comes from `company.name`; stale admin docstring |

Status values: Not started · In progress · Awaiting review · Approved

## Decisions
- Max 3,000 lines total
- Build step by step; approval required between steps
- CSRF protection was built in Step 5 (public form needs it); Step 6 reuses it for admin forms
- Earlier quick draft (`tech_company_site.zip`) is reference only; steps are rebuilt cleanly

## Open items
- Render's default Python is now 3.14; `.python-version` pins 3.12 and `psycopg2-binary` is 2.9.11. If you change Python, re-check that every package in `requirements.txt` supports it
- Smoke test against the real Neon database still needed (SQL was only exercised against a stubbed database since Step 8). Real-browser checks now done in Chromium: no JS or CSP errors, mobile menu, forms, admin
- Minor: after a validation error the consent checkbox is unticked and must be re-checked
- Set `SITE_URL` (your real domain) in Render so canonical links, sitemap and social previews use it
- Check the site in a browser once: the Content-Security-Policy header could not be verified visually
- Run `scripts/init_db.py --seed` and `scripts/create_admin.py` once against the real Neon database and smoke-test it
- Logo: the wordmark is currently the text "Natra Technology" (no logo graphic yet)
- Still placeholder: email (`hello@company.com`) and social links (`#`); location is "Addis Ababa, Ethiopia", confirm it
- Project/portfolio content for Step 3

## Change log
- 2026-10-05: Spec reviewed, task schedule agreed, status document created
- 2026-10-05: Step 1 (Foundation) built; `/` and `/health` verified locally
- 2026-10-05: Step 1 approved; Step 2 (Design system & layout) built
- 2026-10-05: Step 2 approved; Step 3 (Public pages) built, all routes return 200
- 2026-10-05: Step 3 approved; Step 4 (Careers) built
- 2026-10-05: Step 4 approved; Step 5 (Application flow) built
- 2026-10-05: Step 5 approved; Step 6 (Admin auth) built
- 2026-10-05: Step 6 approved; Step 7 (Admin jobs) built; Steps 1-7 verified end to end on a local Postgres
- 2026-10-05: Step 7 approved; Step 8 (Admin applications) built
- 2026-10-05: Step 8 approved; Step 9 (Polish & SEO) built; fixed CSRF empty-token bypass found during testing
- 2026-10-05: Step 9 approved; Step 10 (Deployment docs) built
- 2026-10-05: Step 10 approved; Step 11 (Final QA) run, two small fixes applied
- 2026-10-05: Company name set to Natra Technology, phone set to +251 988 416 048; `og.png` label repainted
- 2026-10-05: Debug pass: fixed Render build failure risk (psycopg2-binary 2.9.9 had no wheels for Render's default Python 3.14; bumped to 2.9.11 and pinned Python 3.12); app now refuses to start in production without `DATABASE_URL`
- 2026-10-05: Real-browser pass (Chromium): fixed `main.js` crash on admin pages (null header), admin header and `.table-wrap` caused ~730px-wide admin pages on phones; 0 overflow across 112 page/width combinations (320-1440px)
