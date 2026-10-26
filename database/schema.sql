-- Neon PostgreSQL schema. Safe to run more than once.
CREATE TABLE IF NOT EXISTS jobs (
    id               SERIAL PRIMARY KEY,
    title            VARCHAR(150) NOT NULL,
    slug             VARCHAR(180) UNIQUE NOT NULL,
    description      TEXT,
    responsibilities TEXT,
    requirements     TEXT,
    location         VARCHAR(100),
    employment_type  VARCHAR(50)  NOT NULL DEFAULT 'Full Time',
    posted_on        DATE NOT NULL DEFAULT CURRENT_DATE,
    deadline         DATE,
    status           VARCHAR(20)  NOT NULL DEFAULT 'draft'
                     CHECK (status IN ('draft', 'published', 'archived')),
    created_at       TIMESTAMPTZ  NOT NULL DEFAULT now(),
    updated_at       TIMESTAMPTZ  NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS applications (
    id         SERIAL PRIMARY KEY,
    job_id     INT          NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    full_name  VARCHAR(100) NOT NULL,
    phone      VARCHAR(20)  NOT NULL,
    consent    BOOLEAN      NOT NULL,
    status     VARCHAR(20)  NOT NULL DEFAULT 'New'
               CHECK (status IN ('New', 'Contacted', 'Interview', 'Hired', 'Rejected')),
    created_at TIMESTAMPTZ  NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ  NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS admins (
    id            SERIAL PRIMARY KEY,
    username      VARCHAR(50) UNIQUE NOT NULL,
    password_hash TEXT        NOT NULL,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);
CREATE INDEX IF NOT EXISTS idx_applications_job ON applications(job_id);
CREATE INDEX IF NOT EXISTS idx_applications_status ON applications(status);

-- Homepage video (managed in Admin > Videos). Only one video can be featured at a time.
CREATE TABLE IF NOT EXISTS videos (
    id          SERIAL PRIMARY KEY,
    title       VARCHAR(150) NOT NULL,
    youtube_id  VARCHAR(11)  NOT NULL,
    description VARCHAR(300),
    thumb_data  BYTEA,                 -- optional custom thumbnail; NULL = use YouTube's own
    thumb_type  VARCHAR(20),
    is_featured BOOLEAN      NOT NULL DEFAULT false,
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ  NOT NULL DEFAULT now()
);
CREATE UNIQUE INDEX IF NOT EXISTS idx_one_featured_video ON videos ((is_featured)) WHERE is_featured;

-- Add columns to databases created before job dates were introduced.
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS posted_on DATE NOT NULL DEFAULT CURRENT_DATE;
ALTER TABLE jobs ADD COLUMN IF NOT EXISTS deadline DATE;

-- Public website content editable from Admin > Website Content.
CREATE TABLE IF NOT EXISTS site_content (
    id SMALLINT PRIMARY KEY CHECK (id = 1),
    content JSONB NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Device-bound offline license request workflow.
CREATE TABLE IF NOT EXISTS license_requests (
 id BIGSERIAL PRIMARY KEY,
 customer_name VARCHAR(120) NOT NULL,
 customer_email VARCHAR(254) NOT NULL,
 product_code VARCHAR(60) NOT NULL,
 hardware_id VARCHAR(180) NOT NULL,
 payment_note VARCHAR(150),
 proof_data BYTEA NOT NULL,
 proof_mime VARCHAR(30) NOT NULL,
 access_hash CHAR(64) NOT NULL UNIQUE,
 status VARCHAR(16) NOT NULL DEFAULT 'pending' CHECK (status IN ('pending','approved','rejected')),
 license_key TEXT,
 admin_note VARCHAR(500),
 approved_by INTEGER REFERENCES admins(id) ON DELETE SET NULL,
 created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
 reviewed_at TIMESTAMPTZ
);
CREATE INDEX IF NOT EXISTS idx_license_requests_status ON license_requests(status, created_at DESC);
