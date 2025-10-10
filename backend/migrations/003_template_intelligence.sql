-- Quest Platform v2.5 - Template Intelligence System
-- Migration: Add 5 new tables for SERP-driven content architecture
-- Run: psql $DATABASE_URL -f 003_template_intelligence.sql

BEGIN;

-- ============================================================================
-- TEMPLATE INTELLIGENCE TABLES
-- ============================================================================

-- 1. Content Archetypes (Strategic Depth Definitions)
-- Defines the 5 archetype patterns with requirements and specifications
CREATE TABLE content_archetypes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL, -- skyscraper, cluster_hub, deep_dive, comparison_matrix, news_hub
    display_name VARCHAR(200) NOT NULL, -- "Skyscraper", "Cluster Hub", etc.
    description TEXT NOT NULL,

    -- Content specifications
    min_word_count INTEGER NOT NULL,
    max_word_count INTEGER NOT NULL,
    min_module_count INTEGER NOT NULL,
    max_module_count INTEGER NOT NULL,
    min_internal_links INTEGER NOT NULL,
    target_keyword_variations INTEGER NOT NULL,

    -- Schema requirements
    required_schemas TEXT[] NOT NULL, -- ['Article', 'FAQPage', 'HowTo']

    -- E-E-A-T requirements (YMYL suitability)
    requires_case_studies BOOLEAN DEFAULT false,
    requires_expert_quotes BOOLEAN DEFAULT false,
    requires_official_sources BOOLEAN DEFAULT false,
    min_citations INTEGER DEFAULT 5,
    ymyl_suitability VARCHAR(50) DEFAULT 'medium', -- low, medium, high, required

    -- Archetype metadata
    strategic_goals TEXT[],
    compatible_templates TEXT[], -- Array of template names

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Seed default archetypes
INSERT INTO content_archetypes (
    name, display_name, description,
    min_word_count, max_word_count, min_module_count, max_module_count,
    min_internal_links, target_keyword_variations,
    required_schemas, requires_case_studies, requires_expert_quotes,
    requires_official_sources, min_citations, ymyl_suitability,
    strategic_goals, compatible_templates
) VALUES
(
    'skyscraper', 'Skyscraper',
    'Comprehensive domain authority hub that dominates a topic',
    8000, 15000, 12, 20, 30, 500,
    ARRAY['Article', 'FAQPage', 'HowTo', 'ItemList'],
    true, true, true, 20, 'required',
    ARRAY['Rank for 500-2000 keyword variations', 'Become definitive resource LLMs cite', 'Maximum E-E-A-T signals'],
    ARRAY['ultimate_guide', 'listicle', 'category_pillar', 'location_guide']
),
(
    'cluster_hub', 'Cluster Hub',
    'Topic navigation center linking to 10-20 deep-dive articles',
    4000, 6000, 8, 12, 10, 200,
    ARRAY['Article', 'CollectionPage', 'ItemList'],
    false, false, true, 10, 'medium',
    ARRAY['Organize topic cluster', 'Provide overview + gateway to detailed content', 'Rank for category keywords'],
    ARRAY['category_pillar', 'ultimate_guide', 'location_guide']
),
(
    'deep_dive', 'Deep Dive Specialist',
    'Definitive answer to ONE specific question/topic',
    3000, 5000, 8, 12, 3, 50,
    ARRAY['Article', 'HowTo', 'FAQPage'],
    true, true, true, 12, 'high',
    ARRAY['Own a specific niche query', 'Maximum depth on single topic', 'Rank #1 for exact-match keywords'],
    ARRAY['deep_dive_tutorial', 'how_to_guide', 'ultimate_guide', 'problem_solution']
),
(
    'comparison_matrix', 'Comparison Matrix',
    'Interactive decision engine for comparing multiple options',
    3000, 4000, 9, 12, 10, 100,
    ARRAY['Article', 'ComparisonTable', 'Review', 'AggregateRating'],
    true, false, true, 10, 'medium',
    ARRAY['Help users make decisions', 'Rank for [X] vs [Y] queries', 'High conversion intent'],
    ARRAY['comparison', 'listicle', 'ultimate_guide']
),
(
    'news_hub', 'News Hub',
    'Living document tracking changes/updates with historical context',
    2000, 3000, 7, 10, 5, 50,
    ARRAY['NewsArticle', 'Article', 'Event'],
    false, false, true, 8, 'medium',
    ARRAY['Rank for timely queries', 'Become go-to source for updates', 'Maintain freshness signals'],
    ARRAY['news_update', 'ultimate_guide', 'problem_solution']
);

-- 2. Content Templates (Visual Structure Definitions)
-- Defines the 12 visual template patterns (user-facing structure)
CREATE TABLE content_templates (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) UNIQUE NOT NULL, -- ultimate_guide, listicle, comparison, etc.
    display_name VARCHAR(200) NOT NULL, -- "Ultimate Guide", "Listicle", etc.
    description TEXT NOT NULL,

    -- Template structure
    visual_pattern VARCHAR(500) NOT NULL, -- "Complete Guide to [Topic]", "Top N [Topic]"
    hero_section_components TEXT[], -- ['breadcrumbs', 'last_updated_badge', 'reading_time']
    content_flow_components TEXT[], -- ['tldr', 'key_stats', 'overview', 'benefits_grid']
    page_features TEXT[], -- ['interactive_calculator', 'downloadable_pdf', 'email_capture']

    -- Schema configuration
    schema_types TEXT[] NOT NULL, -- ['Article', 'HowTo', 'FAQPage', 'BreadcrumbList']

    -- Compatible archetypes
    compatible_archetypes TEXT[], -- Array of archetype names

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Seed priority templates
INSERT INTO content_templates (
    name, display_name, description, visual_pattern,
    hero_section_components, content_flow_components, page_features,
    schema_types, compatible_archetypes
) VALUES
(
    'ultimate_guide', 'Ultimate Guide',
    'Comprehensive guide template with full content hierarchy',
    'Complete Guide to [Topic], Ultimate [Topic] Guide 2025',
    ARRAY['breadcrumbs', 'last_updated_badge', 'reading_time', 'sticky_toc'],
    ARRAY['tldr', 'key_stats', 'overview', 'benefits_grid', 'requirements_checklist', 'step_by_step', 'cost_breakdown', 'comparison', 'faq', 'expert_quotes', 'resources_grid', 'references'],
    ARRAY['interactive_calculator', 'downloadable_pdf', 'email_capture', 'progress_indicator'],
    ARRAY['Article', 'HowTo', 'FAQPage', 'BreadcrumbList'],
    ARRAY['skyscraper', 'cluster_hub', 'deep_dive']
),
(
    'listicle', 'Listicle',
    'Numbered ranking template with at-a-glance summary',
    'Top N [Topic], Best [Options] in 2025',
    ARRAY['number_badge', 'at_a_glance_table'],
    ARRAY['tldr', 'key_takeaways', 'selection_criteria', 'ranked_items', 'comparison_matrix', 'buyers_guide', 'faq', 'references'],
    ARRAY['jump_navigation', 'star_ratings', 'filter_sort', 'comparison_checkboxes'],
    ARRAY['Article', 'ItemList', 'ListItem', 'Review', 'Rating'],
    ARRAY['skyscraper', 'comparison_matrix', 'cluster_hub']
),
(
    'comparison', 'Comparison',
    'Side-by-side comparison template with decision framework',
    '[Option A] vs [Option B], [Topic] Comparison 2025',
    ARRAY['side_by_side_preview', 'quick_verdict', 'winner_badges'],
    ARRAY['tldr', 'key_differences', 'methodology', 'quick_comparison_table', 'option_deep_dives', 'feature_breakdown', 'pricing_comparison', 'decision_framework', 'faq', 'references'],
    ARRAY['interactive_comparison_tool', 'filter_by_criteria', 'save_pdf', 'affiliate_disclosure'],
    ARRAY['Article', 'ComparisonTable', 'Review', 'AggregateRating'],
    ARRAY['comparison_matrix', 'skyscraper']
),
(
    'location_guide', 'Location Guide',
    'City/country-specific guide with map and practical information',
    '[City/Country] Guide for [Audience]',
    ARRAY['interactive_map', 'key_stats_overlay', 'climate_widget'],
    ARRAY['tldr', 'key_takeaways', 'overview', 'best_neighborhoods', 'cost_calculator', 'practical_info', 'coworking_spaces', 'insider_tips', 'expat_community', 'faq', 'references'],
    ARRAY['embedded_google_maps', 'cost_calculator', 'weather_widget', 'currency_converter', 'neighborhood_filter'],
    ARRAY['Article', 'Place', 'TouristDestination', 'LocalBusiness'],
    ARRAY['skyscraper', 'deep_dive']
),
(
    'deep_dive_tutorial', 'Deep Dive Tutorial',
    'Step-by-step how-to guide with detailed instructions',
    'How to [Specific Task], Step-by-Step: [Process]',
    ARRAY['difficulty_badge', 'time_required', 'prerequisites_checklist'],
    ARRAY['tldr', 'prerequisites', 'video_embed', 'step_by_step_process', 'troubleshooting', 'what_next', 'faq', 'references'],
    ARRAY['progress_indicator', 'print_friendly', 'bookmark_tool', 'video_chapters'],
    ARRAY['HowTo', 'HowToStep', 'VideoObject', 'FAQPage'],
    ARRAY['deep_dive', 'skyscraper']
);

-- 3. SERP Intelligence Cache (Competitor Analysis Results)
-- Stores SERP analysis and template recommendations (30-day TTL)
CREATE TABLE serp_intelligence (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    keyword TEXT NOT NULL,
    keyword_hash VARCHAR(64) UNIQUE NOT NULL, -- MD5 hash for fast lookup

    -- SERP data (from Serper.dev)
    serp_results JSONB NOT NULL, -- Top 10 URLs, titles, snippets, positions
    featured_snippet JSONB, -- Featured snippet data if present
    people_also_ask TEXT[], -- PAA questions

    -- Template detection results
    detected_archetype VARCHAR(100) REFERENCES content_archetypes(name),
    recommended_template VARCHAR(100) REFERENCES content_templates(name),
    confidence_score DECIMAL(3,2) CHECK (confidence_score >= 0 AND confidence_score <= 1),

    -- Competitor analysis summary
    avg_word_count INTEGER,
    avg_module_count INTEGER,
    common_modules TEXT[], -- Modules appearing in 2+ competitors
    target_word_count INTEGER,
    target_module_count INTEGER,

    -- Cache metadata
    cache_hits INTEGER DEFAULT 0,
    last_accessed TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ DEFAULT (NOW() + INTERVAL '30 days'),

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for SERP intelligence
CREATE INDEX idx_serp_keyword_hash ON serp_intelligence(keyword_hash);
CREATE INDEX idx_serp_expires ON serp_intelligence(expires_at) WHERE expires_at > NOW();
CREATE INDEX idx_serp_archetype ON serp_intelligence(detected_archetype);

-- 4. Scraped Competitors (Individual Competitor Page Analysis)
-- Stores detailed analysis of each scraped competitor page (from Firecrawl)
CREATE TABLE scraped_competitors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    serp_intelligence_id UUID REFERENCES serp_intelligence(id) ON DELETE CASCADE,

    -- Competitor URL data
    url TEXT NOT NULL,
    position INTEGER NOT NULL, -- Google SERP position
    domain VARCHAR(255),

    -- Content analysis
    word_count INTEGER,
    section_count INTEGER,
    avg_section_depth INTEGER,

    -- Module detection
    modules_found TEXT[], -- ['tldr', 'faq', 'calculator', 'comparison_table']
    module_count INTEGER,

    -- Linking analysis
    internal_links_count INTEGER,
    external_links_count INTEGER,

    -- Schema detection
    schemas_found TEXT[], -- ['Article', 'FAQPage', 'HowTo']
    schema_count INTEGER,

    -- E-E-A-T signals
    has_expert_quotes BOOLEAN DEFAULT false,
    has_case_studies BOOLEAN DEFAULT false,
    has_author_bio BOOLEAN DEFAULT false,
    citations_count INTEGER DEFAULT 0,

    -- Scraped content (full markdown)
    scraped_content TEXT,
    scraped_html TEXT,

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for scraped competitors
CREATE INDEX idx_scraped_serp_id ON scraped_competitors(serp_intelligence_id);
CREATE INDEX idx_scraped_url ON scraped_competitors(url);
CREATE INDEX idx_scraped_position ON scraped_competitors(position);

-- 5. Template Performance (Learning from Results)
-- Tracks performance of archetype/template combinations to improve recommendations
CREATE TABLE template_performance (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    article_id UUID REFERENCES articles(id) ON DELETE CASCADE,

    -- Template intelligence used
    archetype_used VARCHAR(100) REFERENCES content_archetypes(name),
    template_used VARCHAR(100) REFERENCES content_templates(name),
    modules_used TEXT[],

    -- Content metrics
    word_count INTEGER,
    module_count INTEGER,
    quality_score INTEGER,

    -- E-E-A-T metrics
    eeat_score INTEGER CHECK (eeat_score >= 0 AND eeat_score <= 100),
    has_case_studies BOOLEAN DEFAULT false,
    has_expert_quotes BOOLEAN DEFAULT false,
    citations_count INTEGER DEFAULT 0,

    -- Performance metrics (to be updated later via analytics)
    organic_traffic INTEGER DEFAULT 0,
    avg_ranking_position DECIMAL(4,2),
    conversion_rate DECIMAL(5,4),

    -- Audit
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for template performance
CREATE INDEX idx_template_perf_article ON template_performance(article_id);
CREATE INDEX idx_template_perf_archetype ON template_performance(archetype_used);
CREATE INDEX idx_template_perf_template ON template_performance(template_used);
CREATE INDEX idx_template_perf_quality ON template_performance(quality_score DESC);

-- ============================================================================
-- UPDATE EXISTING TABLES
-- ============================================================================

-- Add Template Intelligence columns to articles table (backwards compatible)
ALTER TABLE articles
    ADD COLUMN IF NOT EXISTS target_archetype VARCHAR(100) REFERENCES content_archetypes(name),
    ADD COLUMN IF NOT EXISTS surface_template VARCHAR(100) REFERENCES content_templates(name),
    ADD COLUMN IF NOT EXISTS modules_used TEXT[],
    ADD COLUMN IF NOT EXISTS eeat_score INTEGER CHECK (eeat_score >= 0 AND eeat_score <= 100),
    ADD COLUMN IF NOT EXISTS content_image_1_url TEXT,
    ADD COLUMN IF NOT EXISTS content_image_2_url TEXT,
    ADD COLUMN IF NOT EXISTS content_image_3_url TEXT;

-- Update existing articles to use default template (backwards compatible)
UPDATE articles
SET
    target_archetype = 'skyscraper',
    surface_template = 'ultimate_guide'
WHERE
    target_archetype IS NULL
    AND surface_template IS NULL
    AND status = 'published';

-- Add index for archetype/template filtering
CREATE INDEX idx_articles_archetype_template ON articles(target_archetype, surface_template);

-- ============================================================================
-- VIEWS FOR MONITORING
-- ============================================================================

-- Template intelligence performance summary
CREATE VIEW template_intelligence_summary AS
SELECT
    ta.archetype_used,
    ta.template_used,
    COUNT(*) as total_articles,
    AVG(ta.quality_score) as avg_quality_score,
    AVG(ta.eeat_score) as avg_eeat_score,
    AVG(ta.word_count) as avg_word_count,
    AVG(ta.module_count) as avg_module_count,
    COUNT(*) FILTER (WHERE ta.quality_score >= 85) as high_quality_count,
    COUNT(*) FILTER (WHERE ta.eeat_score >= 80) as strong_eeat_count
FROM template_performance ta
GROUP BY ta.archetype_used, ta.template_used
ORDER BY avg_quality_score DESC;

-- SERP intelligence cache performance
CREATE VIEW serp_cache_performance AS
SELECT
    DATE(created_at) as date,
    COUNT(*) as total_cached_keywords,
    SUM(cache_hits) as total_hits,
    ROUND(100.0 * SUM(cache_hits) / NULLIF(COUNT(*), 0), 2) as hit_rate_pct,
    AVG(confidence_score) as avg_confidence_score,
    COUNT(*) FILTER (WHERE detected_archetype = 'skyscraper') as skyscraper_count,
    COUNT(*) FILTER (WHERE detected_archetype = 'deep_dive') as deep_dive_count,
    COUNT(*) FILTER (WHERE detected_archetype = 'comparison_matrix') as comparison_count
FROM serp_intelligence
WHERE created_at > NOW() - INTERVAL '30 days'
GROUP BY DATE(created_at)
ORDER BY date DESC;

-- E-E-A-T compliance tracking
CREATE VIEW eeat_compliance AS
SELECT
    a.target_site,
    a.target_archetype,
    COUNT(*) as total_articles,
    AVG(tp.eeat_score) as avg_eeat_score,
    COUNT(*) FILTER (WHERE tp.has_case_studies = true) as with_case_studies,
    COUNT(*) FILTER (WHERE tp.has_expert_quotes = true) as with_expert_quotes,
    AVG(tp.citations_count) as avg_citations,
    COUNT(*) FILTER (WHERE tp.eeat_score >= 80) as eeat_compliant_count,
    COUNT(*) FILTER (WHERE tp.eeat_score < 80) as eeat_review_required
FROM articles a
LEFT JOIN template_performance tp ON a.id = tp.article_id
WHERE a.status IN ('published', 'approved')
GROUP BY a.target_site, a.target_archetype;

-- ============================================================================
-- TRIGGERS
-- ============================================================================

-- Auto-update updated_at for archetypes
CREATE TRIGGER update_archetypes_updated_at
    BEFORE UPDATE ON content_archetypes
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Auto-update updated_at for templates
CREATE TRIGGER update_templates_updated_at
    BEFORE UPDATE ON content_templates
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Auto-increment cache_hits on SERP intelligence access
CREATE OR REPLACE FUNCTION increment_serp_cache_hit()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE serp_intelligence
    SET
        cache_hits = cache_hits + 1,
        last_accessed = NOW()
    WHERE id = NEW.id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Note: This trigger is intentionally NOT created here
-- Cache hit tracking will be done manually in TemplateDetector agent

-- ============================================================================
-- SCHEDULED TASKS (pg_cron)
-- ============================================================================

-- Daily SERP cache cleanup (remove expired entries with low usage)
SELECT cron.schedule(
    'serp-cache-cleanup',
    '0 3 * * *',  -- Daily at 3 AM UTC
    $$
        DELETE FROM serp_intelligence
        WHERE expires_at < NOW()
        AND cache_hits < 2;
    $$
);

-- ============================================================================
-- GRANT PERMISSIONS (for Directus user)
-- ============================================================================

-- Directus needs read access to archetypes and templates
GRANT SELECT ON content_archetypes TO directus_user;
GRANT SELECT ON content_templates TO directus_user;
GRANT SELECT ON serp_intelligence TO directus_user;
GRANT SELECT ON template_performance TO directus_user;

-- Directus can view but not modify scraped competitors
GRANT SELECT ON scraped_competitors TO directus_user;

COMMIT;

-- ============================================================================
-- POST-DEPLOYMENT VALIDATION
-- ============================================================================

-- Verify new tables created
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN ('content_archetypes', 'content_templates', 'serp_intelligence', 'scraped_competitors', 'template_performance')
ORDER BY table_name;

-- Verify archetypes seeded
SELECT name, display_name, min_word_count, max_word_count, ymyl_suitability
FROM content_archetypes
ORDER BY min_word_count DESC;

-- Verify templates seeded
SELECT name, display_name, array_length(schema_types, 1) as schema_count
FROM content_templates
ORDER BY name;

-- Verify articles table updated
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'articles'
AND column_name IN ('target_archetype', 'surface_template', 'modules_used', 'eeat_score')
ORDER BY column_name;

-- Verify indexes created
SELECT tablename, indexname
FROM pg_indexes
WHERE schemaname = 'public'
AND tablename IN ('serp_intelligence', 'scraped_competitors', 'template_performance', 'articles')
ORDER BY tablename, indexname;

COMMENT ON TABLE content_archetypes IS 'Template Intelligence System: Content archetype definitions (strategic depth)';
COMMENT ON TABLE content_templates IS 'Template Intelligence System: Visual template definitions (user-facing structure)';
COMMENT ON TABLE serp_intelligence IS 'Template Intelligence System: SERP analysis cache (30-day TTL)';
COMMENT ON TABLE scraped_competitors IS 'Template Intelligence System: Individual competitor page analysis';
COMMENT ON TABLE template_performance IS 'Template Intelligence System: Performance tracking for learning';
