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
