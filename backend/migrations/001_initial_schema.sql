-- Quest Platform v2.2 - Initial Schema
-- Database-First Architecture for Neon PostgreSQL 16
-- Run: psql $DATABASE_URL -f 001_initial_schema.sql

BEGIN;

-- ============================================================================
-- EXTENSIONS
-- ============================================================================

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";           -- UUID generation
CREATE EXTENSION IF NOT EXISTS "pg_trgm";             -- Fuzzy text search
CREATE EXTENSION IF NOT EXISTS "vector";              -- pgvector for embeddings
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";  -- Query performance monitoring
CREATE EXTENSION IF NOT EXISTS "btree_gin";           -- GIN indexes for arrays
CREATE EXTENSION IF NOT EXISTS "pg_cron";             -- Scheduled tasks

-- ============================================================================
-- CORE TABLES
-- ============================================================================

-- Users (for Directus auth + article authors)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    role VARCHAR(50) DEFAULT 'editor', -- admin, editor, viewer
    avatar_url TEXT,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_login TIMESTAMPTZ
);

-- Create default admin user (password will be set via Directus)
INSERT INTO users (email, first_name, last_name, role)
VALUES ('admin@quest.com', 'Quest', 'Admin', 'admin');

-- Articles (main content table)
CREATE TABLE articles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    content TEXT NOT NULL,
    excerpt TEXT,
    hero_image_url TEXT,

    -- Multi-site support
    target_site VARCHAR(50) NOT NULL CHECK (target_site IN ('relocation', 'placement', 'rainmaker')),

    -- Metadata
    status VARCHAR(20) DEFAULT 'draft' CHECK (status IN ('draft', 'review', 'approved', 'published', 'archived')),
    quality_score INTEGER CHECK (quality_score >= 0 AND quality_score <= 100),
    reading_time_minutes INTEGER,

    -- SEO
    meta_title TEXT,
    meta_description TEXT,
    keywords TEXT[],

    -- Publishing
    published_date TIMESTAMPTZ,
    author_id UUID REFERENCES users(id) ON DELETE SET NULL,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for articles
CREATE INDEX idx_articles_site_status ON articles(target_site, status);
CREATE INDEX idx_articles_published ON articles(published_date DESC) WHERE status = 'published';
CREATE INDEX idx_articles_slug ON articles(slug);
CREATE INDEX idx_articles_keywords ON articles USING GIN(keywords);

-- Research Cache (vector similarity search)
CREATE TABLE article_research (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    topic_query TEXT NOT NULL,
    embedding vector(1536), -- OpenAI text-embedding-ada-002

    -- Research data
    research_json JSONB NOT NULL,
    source_urls TEXT[],

    -- Cache metadata
    embedding_model_version VARCHAR(50) DEFAULT 'text-embedding-ada-002',
    cache_hits INTEGER DEFAULT 0,
    last_accessed TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ DEFAULT (NOW() + INTERVAL '30 days'),

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for research cache
CREATE INDEX idx_research_topic ON article_research USING GIN(to_tsvector('english', topic_query));
CREATE INDEX idx_research_embedding ON article_research USING ivfflat(embedding vector_cosine_ops) WITH (lists = 100);
CREATE INDEX idx_research_expires ON article_research(expires_at) WHERE expires_at > NOW();

-- Job Status (BullMQ tracking)
CREATE TABLE job_status (
    job_id VARCHAR(255) PRIMARY KEY,
    article_id UUID REFERENCES articles(id) ON DELETE CASCADE,

    status VARCHAR(50) NOT NULL CHECK (status IN ('queued', 'processing', 'completed', 'failed')),
    progress INTEGER DEFAULT 0 CHECK (progress >= 0 AND progress <= 100),
    current_step VARCHAR(100), -- research, content, editor, image

    -- Cost tracking
    cost_breakdown JSONB DEFAULT '{}',
    total_cost DECIMAL(10,4) DEFAULT 0,

    -- Error handling
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,

    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ
);

-- Indexes for job status
CREATE INDEX idx_job_status ON job_status(status, created_at DESC);
CREATE INDEX idx_job_article ON job_status(article_id);

-- ============================================================================
-- VIEWS FOR MONITORING
-- ============================================================================

-- Daily cost tracking
CREATE VIEW daily_costs AS
SELECT
    DATE(created_at) as date,
    COUNT(*) as articles_generated,
    SUM((cost_breakdown->>'research')::decimal) as research_cost,
    SUM((cost_breakdown->>'content')::decimal) as content_cost,
    SUM((cost_breakdown->>'editor')::decimal) as editor_cost,
    SUM((cost_breakdown->>'image')::decimal) as image_cost,
    SUM(total_cost) as total_cost,
    AVG(total_cost) as avg_cost_per_article
FROM job_status
WHERE status = 'completed'
GROUP BY DATE(created_at)
ORDER BY date DESC;

-- Cache performance metrics
CREATE VIEW cache_performance AS
SELECT
    DATE(last_accessed) as date,
    COUNT(*) as total_cached_topics,
    SUM(cache_hits) as total_hits,
    ROUND(100.0 * SUM(cache_hits) / NULLIF(COUNT(*), 0), 2) as hit_rate_pct,
    ROUND(SUM(cache_hits) * 0.20, 2) as estimated_savings_usd
FROM article_research
WHERE last_accessed > NOW() - INTERVAL '30 days'
GROUP BY DATE(last_accessed)
ORDER BY date DESC;

-- Article quality distribution
CREATE VIEW quality_distribution AS
SELECT
    target_site,
    COUNT(*) as total_articles,
    AVG(quality_score) as avg_quality_score,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY quality_score) as median_quality_score,
    COUNT(*) FILTER (WHERE quality_score >= 85) as auto_published_count,
    COUNT(*) FILTER (WHERE quality_score BETWEEN 70 AND 84) as review_required_count,
    COUNT(*) FILTER (WHERE quality_score < 70) as rejected_count
FROM articles
WHERE quality_score IS NOT NULL
GROUP BY target_site;

-- ============================================================================
-- TRIGGERS
-- ============================================================================

-- Auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_articles_updated_at
    BEFORE UPDATE ON articles
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Auto-generate slug from title if not provided
CREATE OR REPLACE FUNCTION generate_slug_from_title()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.slug IS NULL OR NEW.slug = '' THEN
        NEW.slug := lower(regexp_replace(NEW.title, '[^a-zA-Z0-9]+', '-', 'g'));
        NEW.slug := trim(both '-' from NEW.slug);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER generate_article_slug
    BEFORE INSERT ON articles
    FOR EACH ROW
    EXECUTE FUNCTION generate_slug_from_title();

-- ============================================================================
-- SCHEDULED TASKS (pg_cron)
-- ============================================================================

-- Daily cache cleanup (remove expired entries with low usage)
SELECT cron.schedule(
    'cache-cleanup',
    '0 2 * * *',  -- Daily at 2 AM UTC
    $$
        DELETE FROM article_research
        WHERE expires_at < NOW()
        AND cache_hits < 3;
    $$
);

-- Weekly stats summary (for monitoring)
SELECT cron.schedule(
    'weekly-stats',
    '0 9 * * 1',  -- Monday at 9 AM UTC
    $$
        INSERT INTO job_status (job_id, status, current_step, created_at)
        VALUES (
            'weekly-stats-' || NOW()::TEXT,
            'completed',
            'stats',
            NOW()
        );
    $$
);

-- ============================================================================
-- GRANT PERMISSIONS (Run after creating users in 002_create_users.sql)
-- ============================================================================

-- Note: These will be executed after users are created
-- See 002_create_users.sql for actual permission grants

COMMIT;

-- ============================================================================
-- POST-DEPLOYMENT VALIDATION
-- ============================================================================

-- Verify extensions
SELECT extname, extversion FROM pg_extension WHERE extname IN ('uuid-ossp', 'vector', 'pg_trgm', 'pg_stat_statements', 'btree_gin', 'pg_cron');

-- Verify tables
SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name;

-- Verify indexes
SELECT tablename, indexname FROM pg_indexes WHERE schemaname = 'public' ORDER BY tablename, indexname;

-- Test vector similarity (should return empty result set)
SELECT 1 FROM article_research WHERE 1 - (embedding <=> '[0,0,0]'::vector) > 0.75 LIMIT 1;

COMMENT ON DATABASE neondb IS 'Quest Platform v2.2 - Production Database';
