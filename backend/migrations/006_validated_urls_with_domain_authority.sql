-- Migration 006: Validated URLs with Domain Authority
-- Created: October 11, 2025
-- Purpose: Build permanent cache of validated URLs with DA scores for SEO optimization

-- Core insight: Authority signal front-loading
-- Link to high-DA sites (especially competitors!) in first paragraph for trust signals

CREATE TABLE IF NOT EXISTS validated_urls (
    id SERIAL PRIMARY KEY,
    url TEXT NOT NULL,
    url_hash VARCHAR(64) UNIQUE NOT NULL,  -- SHA256 for fast lookup
    domain TEXT NOT NULL,

    -- Domain Authority Metrics (from DataForSEO Backlinks API)
    domain_authority INTEGER,  -- 0-100 (DataForSEO "rank" field)
    page_authority INTEGER,  -- 0-100 (page-specific if available)
    backlinks_count BIGINT,  -- Total backlinks to domain
    referring_domains_count INTEGER,  -- Unique domains linking
    organic_traffic_estimate INTEGER,  -- Monthly organic visitors
    spam_score INTEGER DEFAULT 0,  -- 0-100 (higher = spammier)

    -- Authority Classification (for content agent routing)
    authority_class VARCHAR(20),  -- 'ultra_high' (90+), 'high' (70-89), 'medium' (50-69), 'low' (<50)
    is_tier1_signal BOOLEAN DEFAULT FALSE,  -- BBC, Reuters, Wikipedia, NYT, .gov
    is_wikipedia BOOLEAN DEFAULT FALSE,  -- Special flag for Wikipedia (highest trust)
    is_reddit BOOLEAN DEFAULT FALSE,  -- Special flag for Reddit (community validation)
    is_competitor BOOLEAN DEFAULT FALSE,  -- NEW: Sites ranking on page 1 for our keywords
    serp_position INTEGER,  -- Position in SERP (1-100, null if not competitor)

    -- Validation History
    first_validated_at TIMESTAMPTZ DEFAULT NOW(),
    last_validated_at TIMESTAMPTZ DEFAULT NOW(),
    last_da_check TIMESTAMPTZ,  -- Track when we last fetched DA (expensive, cache 30 days)
    last_check_status INTEGER,  -- Last HTTP status code
    consecutive_successes INTEGER DEFAULT 1,
    consecutive_failures INTEGER DEFAULT 0,
    total_validations INTEGER DEFAULT 1,

    -- Trust Metrics (composite score)
    trust_score INTEGER DEFAULT 50,  -- Our calculated 0-100 score
    authority_tier INTEGER,  -- 1-4 based on DA + context

    -- Usage Tracking
    times_referenced INTEGER DEFAULT 0,
    articles_used_in TEXT[],  -- Array of article UUIDs
    target_sites TEXT[],  -- Which sites used this (relocation, placement, rainmaker)
    times_used_in_intro INTEGER DEFAULT 0,  -- How many times in first 500 words
    avg_position_in_article INTEGER,  -- Average paragraph number

    -- Quality Indicators
    has_https BOOLEAN DEFAULT TRUE,
    has_valid_ssl BOOLEAN DEFAULT TRUE,
    avg_response_time_ms INTEGER,
    content_type TEXT,  -- text/html, application/pdf, etc.
    page_title TEXT,
    meta_description TEXT,
    last_modified TIMESTAMPTZ,

    -- Blocklist
    is_blocked BOOLEAN DEFAULT FALSE,
    blocked_reason TEXT,
    blocked_at TIMESTAMPTZ,

    -- Metadata
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for fast lookups
CREATE INDEX IF NOT EXISTS idx_validated_urls_hash ON validated_urls(url_hash);
CREATE INDEX IF NOT EXISTS idx_validated_urls_domain ON validated_urls(domain);
CREATE INDEX IF NOT EXISTS idx_validated_urls_da ON validated_urls(domain_authority DESC) WHERE domain_authority IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_validated_urls_authority_class ON validated_urls(authority_class);
CREATE INDEX IF NOT EXISTS idx_validated_urls_tier1 ON validated_urls(is_tier1_signal) WHERE is_tier1_signal = TRUE;
CREATE INDEX IF NOT EXISTS idx_validated_urls_competitor ON validated_urls(is_competitor) WHERE is_competitor = TRUE;
CREATE INDEX IF NOT EXISTS idx_validated_urls_trust_score ON validated_urls(trust_score DESC);
CREATE INDEX IF NOT EXISTS idx_validated_urls_last_validated ON validated_urls(last_validated_at);

-- Function to calculate URL hash (for upserts)
CREATE OR REPLACE FUNCTION calculate_url_hash(url_text TEXT)
RETURNS VARCHAR(64) AS $$
BEGIN
    RETURN encode(digest(url_text, 'sha256'), 'hex');
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_validated_urls_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER validated_urls_update_timestamp
    BEFORE UPDATE ON validated_urls
    FOR EACH ROW
    EXECUTE FUNCTION update_validated_urls_timestamp();

-- Seed with Tier 1 authority sites (ultra-high DA 90+)
INSERT INTO validated_urls (
    url, url_hash, domain, domain_authority, authority_class,
    is_tier1_signal, is_wikipedia, trust_score, authority_tier
) VALUES
    -- Knowledge Bases
    ('https://en.wikipedia.org', calculate_url_hash('https://en.wikipedia.org'), 'en.wikipedia.org', 98, 'ultra_high', TRUE, TRUE, 98, 1),
    ('https://wikipedia.org', calculate_url_hash('https://wikipedia.org'), 'wikipedia.org', 98, 'ultra_high', TRUE, TRUE, 98, 1),

    -- News Organizations
    ('https://bbc.com', calculate_url_hash('https://bbc.com'), 'bbc.com', 96, 'ultra_high', TRUE, FALSE, 96, 1),
    ('https://bbc.co.uk', calculate_url_hash('https://bbc.co.uk'), 'bbc.co.uk', 96, 'ultra_high', TRUE, FALSE, 96, 1),
    ('https://reuters.com', calculate_url_hash('https://reuters.com'), 'reuters.com', 95, 'ultra_high', TRUE, FALSE, 95, 1),
    ('https://nytimes.com', calculate_url_hash('https://nytimes.com'), 'nytimes.com', 95, 'ultra_high', TRUE, FALSE, 95, 1),
    ('https://theguardian.com', calculate_url_hash('https://theguardian.com'), 'theguardian.com', 94, 'ultra_high', TRUE, FALSE, 94, 1),
    ('https://economist.com', calculate_url_hash('https://economist.com'), 'economist.com', 93, 'ultra_high', TRUE, FALSE, 93, 1),

    -- Government & International Orgs
    ('https://europa.eu', calculate_url_hash('https://europa.eu'), 'europa.eu', 94, 'ultra_high', TRUE, FALSE, 94, 1),
    ('https://oecd.org', calculate_url_hash('https://oecd.org'), 'oecd.org', 92, 'ultra_high', TRUE, FALSE, 92, 1),
    ('https://worldbank.org', calculate_url_hash('https://worldbank.org'), 'worldbank.org', 93, 'ultra_high', TRUE, FALSE, 93, 1),
    ('https://imf.org', calculate_url_hash('https://imf.org'), 'imf.org', 91, 'ultra_high', TRUE, FALSE, 91, 1),

    -- Community
    ('https://reddit.com', calculate_url_hash('https://reddit.com'), 'reddit.com', 95, 'ultra_high', TRUE, FALSE, 95, 1)
ON CONFLICT (url_hash) DO NOTHING;

-- Comments
COMMENT ON TABLE validated_urls IS 'Permanent cache of validated URLs with Domain Authority scores for SEO optimization';
COMMENT ON COLUMN validated_urls.domain_authority IS 'DataForSEO domain rank 0-100 (equivalent to MOZ DA)';
COMMENT ON COLUMN validated_urls.is_competitor IS 'Sites ranking on page 1 for our target keywords (link to them for authority!)';
COMMENT ON COLUMN validated_urls.trust_score IS 'Composite 0-100 score: DA (40%) + validation history (25%) + performance (20%) + quality (15%)';
COMMENT ON COLUMN validated_urls.times_used_in_intro IS 'Count of times used in first 500 words (critical for authority signal front-loading)';
