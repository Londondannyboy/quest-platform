-- Quest Platform v2.6 - Cluster Research Cost Optimization
-- Migration: Add topic clusters and cluster research caching
-- Purpose: Reduce research costs by 54% ($325/month savings)

BEGIN;

-- ============================================================================
-- TOPIC CLUSTERS (Content Strategy Organization)
-- ============================================================================

CREATE TABLE topic_clusters (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    slug VARCHAR(200) UNIQUE NOT NULL,
    description TEXT,

    -- Strategy
    priority VARCHAR(20) CHECK (priority IN ('high', 'medium', 'low')) DEFAULT 'medium',
    target_site VARCHAR(50) NOT NULL, -- relocation, placement, rainmaker

    -- Keywords in this cluster
    primary_keywords TEXT[] NOT NULL,
    secondary_keywords TEXT[],

    -- Research settings
    research_tier VARCHAR(20) CHECK (research_tier IN ('perplexity', 'tavily', 'haiku')) DEFAULT 'tavily',
    research_ttl_days INTEGER DEFAULT 90,

    -- Metrics
    article_count INTEGER DEFAULT 0,
    total_research_cost DECIMAL(10,2) DEFAULT 0,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Index for fast keyword lookups
CREATE INDEX idx_clusters_keywords ON topic_clusters USING GIN(primary_keywords);
CREATE INDEX idx_clusters_priority ON topic_clusters(priority, target_site);

-- ============================================================================
-- CLUSTER RESEARCH (Reusable Research Cache)
-- ============================================================================

CREATE TABLE cluster_research (
    id SERIAL PRIMARY KEY,
    cluster_id INTEGER REFERENCES topic_clusters(id) ON DELETE CASCADE,

    -- Research data
    research_data JSONB NOT NULL,
    keywords_analyzed TEXT[],

    -- SEO foundation (DataForSEO results)
    seo_data JSONB,
    search_volume INTEGER,
    keyword_difficulty INTEGER,

    -- SERP analysis
    serp_analysis JSONB,
    top_ranking_urls TEXT[],

    -- AI insights (Perplexity/Tavily/Haiku)
    ai_insights JSONB,
    ai_provider VARCHAR(50), -- perplexity, tavily, haiku

    -- Cost tracking
    research_cost DECIMAL(10,2) NOT NULL,

    -- Usage tracking
    reuse_count INTEGER DEFAULT 0,
    last_used_at TIMESTAMPTZ DEFAULT NOW(),

    -- Cache management
    expires_at TIMESTAMPTZ DEFAULT (NOW() + INTERVAL '90 days'),
    is_stale BOOLEAN DEFAULT false,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_cluster_research_cluster ON cluster_research(cluster_id);
CREATE INDEX idx_cluster_research_expiry ON cluster_research(expires_at) WHERE NOT is_stale;
CREATE INDEX idx_cluster_research_reuse ON cluster_research(cluster_id, reuse_count DESC);

-- ============================================================================
-- ENHANCE EXISTING TABLES
-- ============================================================================

-- Link articles to clusters
ALTER TABLE articles
    ADD COLUMN IF NOT EXISTS cluster_id INTEGER REFERENCES topic_clusters(id),
    ADD COLUMN IF NOT EXISTS cluster_research_id INTEGER REFERENCES cluster_research(id),
    ADD COLUMN IF NOT EXISTS research_cost DECIMAL(10,2) DEFAULT 0;

-- Index for cluster analysis
CREATE INDEX idx_articles_cluster ON articles(cluster_id, status);

-- Link existing article_research to clusters (backward compatibility)
ALTER TABLE article_research
    ADD COLUMN IF NOT EXISTS cluster_id INTEGER REFERENCES topic_clusters(id),
    ADD COLUMN IF NOT EXISTS is_cluster_research BOOLEAN DEFAULT false;

-- ============================================================================
-- VIEWS FOR MONITORING
-- ============================================================================

-- Cluster performance and cost savings
CREATE VIEW cluster_cost_analysis AS
SELECT
    tc.name as cluster_name,
    tc.priority,
    tc.target_site,
    tc.article_count,
    tc.total_research_cost,

    -- Cluster research stats
    cr.research_cost as initial_research_cost,
    cr.reuse_count,
    cr.created_at as research_date,
    cr.expires_at as research_expiry,

    -- Cost calculations
    (tc.article_count * 0.45) as cost_if_no_reuse,
    tc.total_research_cost as actual_cost,
    ((tc.article_count * 0.45) - tc.total_research_cost) as cost_saved,

    -- ROI metrics
    CASE
        WHEN tc.article_count > 0
        THEN ROUND((tc.total_research_cost / tc.article_count)::numeric, 2)
        ELSE 0
    END as cost_per_article
FROM topic_clusters tc
LEFT JOIN LATERAL (
    SELECT * FROM cluster_research
    WHERE cluster_id = tc.id
    ORDER BY created_at DESC
    LIMIT 1
) cr ON true
ORDER BY tc.article_count DESC;

-- Research reuse efficiency
CREATE VIEW research_reuse_stats AS
SELECT
    DATE(cr.created_at) as research_date,
    COUNT(*) as clusters_researched,
    SUM(cr.reuse_count) as total_reuses,
    SUM(cr.research_cost) as research_investment,
    SUM(cr.reuse_count * 0.45) as cost_savings,
    ROUND(AVG(cr.reuse_count), 1) as avg_reuse_per_cluster
FROM cluster_research cr
WHERE cr.created_at > NOW() - INTERVAL '30 days'
GROUP BY DATE(cr.created_at)
ORDER BY research_date DESC;

-- ============================================================================
-- TRIGGERS
-- ============================================================================

-- Auto-update cluster article count
CREATE OR REPLACE FUNCTION update_cluster_article_count()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.cluster_id IS NOT NULL THEN
        UPDATE topic_clusters
        SET
            article_count = article_count + 1,
            total_research_cost = total_research_cost + COALESCE(NEW.research_cost, 0),
            updated_at = NOW()
        WHERE id = NEW.cluster_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_cluster_count
    AFTER INSERT ON articles
    FOR EACH ROW
    EXECUTE FUNCTION update_cluster_article_count();

-- Auto-increment research reuse count
CREATE OR REPLACE FUNCTION increment_research_reuse()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.cluster_research_id IS NOT NULL THEN
        UPDATE cluster_research
        SET
            reuse_count = reuse_count + 1,
            last_used_at = NOW()
        WHERE id = NEW.cluster_research_id;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_increment_reuse
    AFTER INSERT ON articles
    FOR EACH ROW
    EXECUTE FUNCTION increment_research_reuse();

-- ============================================================================
-- SEED DATA (From QUEST_RELOCATION_RESEARCH.md)
-- ============================================================================

-- High priority clusters (Perplexity research)
INSERT INTO topic_clusters (name, slug, description, priority, target_site, primary_keywords, research_tier) VALUES
('Portugal Digital Nomad', 'portugal-digital-nomad', 'Portugal visa, residency, and relocation content', 'high', 'relocation',
 ARRAY['portugal digital nomad visa', 'portugal d7 visa', 'portugal residence permit', 'living in portugal'], 'perplexity'),

('Spain Digital Nomad', 'spain-digital-nomad', 'Spain visa, residency, and remote work content', 'high', 'relocation',
 ARRAY['spain digital nomad visa', 'spain visa requirements', 'living in spain', 'spain remote work'], 'perplexity'),

('Italy Golden Visa', 'italy-golden-visa', 'Italy investment and residency content', 'high', 'relocation',
 ARRAY['italy golden visa', 'italy investor visa', 'italy residence permit'], 'perplexity'),

('Greece Golden Visa', 'greece-golden-visa', 'Greece investment and residency content', 'high', 'relocation',
 ARRAY['greece golden visa', 'greece investor visa', 'greece residence permit'], 'perplexity');

-- Medium priority clusters (Tavily research - cheaper)
INSERT INTO topic_clusters (name, slug, description, priority, target_site, primary_keywords, research_tier) VALUES
('Remote Work Europe', 'remote-work-europe', 'General European remote work content', 'medium', 'relocation',
 ARRAY['remote work europe', 'work from europe', 'digital nomad europe'], 'tavily'),

('Tax Optimization', 'tax-optimization', 'Tax residency and optimization content', 'medium', 'relocation',
 ARRAY['tax residency', 'tax optimization', 'digital nomad taxes'], 'tavily'),

('Healthcare Abroad', 'healthcare-abroad', 'International healthcare and insurance', 'medium', 'relocation',
 ARRAY['expat healthcare', 'international health insurance', 'healthcare abroad'], 'tavily');

-- Low priority clusters (Haiku synthesis only - cheapest)
INSERT INTO topic_clusters (name, slug, description, priority, target_site, primary_keywords, research_tier) VALUES
('Culture & Lifestyle', 'culture-lifestyle', 'Cultural adaptation and lifestyle content', 'low', 'relocation',
 ARRAY['expat life', 'culture shock', 'living abroad'], 'haiku'),

('Language Learning', 'language-learning', 'Language learning for expats', 'low', 'relocation',
 ARRAY['learn portuguese', 'learn spanish', 'language learning abroad'], 'haiku');

-- ============================================================================
-- FUNCTIONS FOR RESEARCH GOVERNANCE
-- ============================================================================

-- Find cluster for a topic (smart matching)
CREATE OR REPLACE FUNCTION find_cluster_for_topic(p_topic TEXT)
RETURNS INTEGER AS $$
DECLARE
    v_cluster_id INTEGER;
BEGIN
    -- Try exact keyword match first
    SELECT id INTO v_cluster_id
    FROM topic_clusters
    WHERE p_topic ILIKE ANY(primary_keywords)
       OR p_topic ILIKE ANY(secondary_keywords)
    LIMIT 1;

    -- Fallback to similarity search
    IF v_cluster_id IS NULL THEN
        SELECT id INTO v_cluster_id
        FROM topic_clusters
        WHERE p_topic % ANY(primary_keywords)  -- Fuzzy match
        ORDER BY similarity(p_topic, name) DESC
        LIMIT 1;
    END IF;

    RETURN v_cluster_id;
END;
$$ LANGUAGE plpgsql;

-- Check if cluster has recent research
CREATE OR REPLACE FUNCTION cluster_has_recent_research(p_cluster_id INTEGER)
RETURNS BOOLEAN AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1 FROM cluster_research
        WHERE cluster_id = p_cluster_id
          AND expires_at > NOW()
          AND NOT is_stale
    );
END;
$$ LANGUAGE plpgsql;

COMMIT;

-- ============================================================================
-- POST-DEPLOYMENT VALIDATION
-- ============================================================================

-- Verify tables created
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN ('topic_clusters', 'cluster_research')
ORDER BY table_name;

-- Verify clusters seeded
SELECT name, priority, research_tier, array_length(primary_keywords, 1) as keyword_count
FROM topic_clusters
ORDER BY priority DESC, name;

-- Verify functions created
SELECT routine_name FROM information_schema.routines
WHERE routine_schema = 'public'
AND routine_name IN ('find_cluster_for_topic', 'cluster_has_recent_research')
ORDER BY routine_name;

COMMENT ON TABLE topic_clusters IS 'Cost Optimization: Topic clusters for research reuse (54% savings potential)';
COMMENT ON TABLE cluster_research IS 'Cost Optimization: Cached cluster research (90-day TTL, tracks reuse)';
