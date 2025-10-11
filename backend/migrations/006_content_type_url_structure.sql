-- Migration 006: Content-Type-Based URL Structure
-- Date: October 11, 2025
-- Purpose: Add content_type column and country field for semantic URL generation
-- Related: QUEST_URL_STRUCTURE.md

BEGIN;

-- ============================================================================
-- STEP 1: Add content_type column with default
-- ============================================================================

ALTER TABLE articles
ADD COLUMN content_type VARCHAR(50) DEFAULT 'guide';

COMMENT ON COLUMN articles.content_type IS 'Content type for URL generation: guide, comparison, listicle, deep-dive, country-hub, market-report, case-study, playbook, interview-guide, conversational';

-- ============================================================================
-- STEP 2: Add country column for location-specific content
-- ============================================================================

ALTER TABLE articles
ADD COLUMN country VARCHAR(100);

COMMENT ON COLUMN articles.country IS 'ISO country code or name for location-specific content (e.g., "portugal", "germany")';

-- ============================================================================
-- STEP 3: Backfill content_type based on existing data
-- ============================================================================

-- Detect comparisons (contains "vs" or "versus" in title/slug)
UPDATE articles
SET content_type = 'comparison'
WHERE (
    title ILIKE '%vs%' OR
    title ILIKE '%versus%' OR
    slug LIKE '%vs-%'
) AND content_type = 'guide';

-- Detect listicles (title starts with "Top X" or "Best X")
UPDATE articles
SET content_type = 'listicle'
WHERE (
    title ~* '^(Top|Best) \d+' OR
    slug ~* '^top-\d+'
) AND content_type = 'guide';

-- Detect deep dives (contains analysis keywords)
UPDATE articles
SET content_type = 'deep-dive'
WHERE (
    title ILIKE '%implications%' OR
    title ILIKE '%analysis%' OR
    title ILIKE '%breakdown%' OR
    title ILIKE '%deep dive%'
) AND content_type = 'guide';

-- Detect country hubs (title contains country name + "digital nomad" or "expat")
UPDATE articles
SET content_type = 'country-hub'
WHERE (
    (title ILIKE '%portugal%' OR title ILIKE '%spain%' OR title ILIKE '%italy%' OR title ILIKE '%germany%') AND
    (title ILIKE '%digital nomad%' OR title ILIKE '%expat%' OR title ILIKE '%living in%')
) AND content_type = 'guide';

-- ============================================================================
-- STEP 4: Extract country from titles/slugs
-- ============================================================================

-- Extract country from common patterns
UPDATE articles
SET country =
    CASE
        WHEN title ILIKE '%portugal%' OR slug LIKE '%portugal%' THEN 'portugal'
        WHEN title ILIKE '%spain%' OR slug LIKE '%spain%' THEN 'spain'
        WHEN title ILIKE '%italy%' OR slug LIKE '%italy%' THEN 'italy'
        WHEN title ILIKE '%germany%' OR slug LIKE '%germany%' THEN 'germany'
        WHEN title ILIKE '%france%' OR slug LIKE '%france%' THEN 'france'
        WHEN title ILIKE '%croatia%' OR slug LIKE '%croatia%' THEN 'croatia'
        WHEN title ILIKE '%greece%' OR slug LIKE '%greece%' THEN 'greece'
        WHEN title ILIKE '%iceland%' OR slug LIKE '%iceland%' THEN 'iceland'
        WHEN title ILIKE '%netherlands%' OR slug LIKE '%netherlands%' THEN 'netherlands'
        WHEN title ILIKE '%estonia%' OR slug LIKE '%estonia%' THEN 'estonia'
        ELSE NULL
    END
WHERE country IS NULL;

-- ============================================================================
-- STEP 5: Update slugs to include content_type prefix (NON-BREAKING)
-- ============================================================================

-- NOTE: This does NOT update existing slugs to avoid breaking live URLs
-- New articles will use the content_type prefix automatically
-- Old articles keep their original slugs for backwards compatibility

-- Create a new column for the new URL format (optional, for migration tracking)
ALTER TABLE articles
ADD COLUMN new_slug TEXT;

-- Generate new slugs with content_type prefix
UPDATE articles
SET new_slug =
    CASE
        WHEN target_site = 'placement' AND country IS NOT NULL
            THEN content_type || '/' || country || '/' ||
                 REGEXP_REPLACE(slug, '^(' || content_type || '/' || country || '/)?', '')
        ELSE content_type || '/' ||
             REGEXP_REPLACE(slug, '^(' || content_type || '/)?', '')
    END;

-- ============================================================================
-- STEP 6: Create indexes for performance
-- ============================================================================

CREATE INDEX idx_articles_content_type ON articles(content_type);
CREATE INDEX idx_articles_country ON articles(country) WHERE country IS NOT NULL;
CREATE INDEX idx_articles_site_content_type ON articles(target_site, content_type);

-- ============================================================================
-- STEP 7: Make content_type NOT NULL after backfill
-- ============================================================================

ALTER TABLE articles
ALTER COLUMN content_type SET NOT NULL;

-- ============================================================================
-- STEP 8: Create view for content type analytics
-- ============================================================================

CREATE OR REPLACE VIEW content_type_summary AS
SELECT
    target_site,
    content_type,
    COUNT(*) as article_count,
    AVG(quality_score) as avg_quality,
    AVG(LENGTH(content)) as avg_word_count,
    COUNT(*) FILTER (WHERE status = 'published') as published_count,
    COUNT(*) FILTER (WHERE created_at > NOW() - INTERVAL '30 days') as recent_count
FROM articles
GROUP BY target_site, content_type
ORDER BY target_site, article_count DESC;

COMMENT ON VIEW content_type_summary IS 'Analytics view showing content type distribution and quality metrics per site';

-- ============================================================================
-- VALIDATION: Check migration results
-- ============================================================================

DO $$
DECLARE
    total_articles INTEGER;
    articles_with_type INTEGER;
    articles_with_country INTEGER;
BEGIN
    SELECT COUNT(*) INTO total_articles FROM articles;
    SELECT COUNT(*) INTO articles_with_type FROM articles WHERE content_type IS NOT NULL;
    SELECT COUNT(*) INTO articles_with_country FROM articles WHERE country IS NOT NULL;

    RAISE NOTICE 'Migration 006 Validation:';
    RAISE NOTICE '  Total articles: %', total_articles;
    RAISE NOTICE '  Articles with content_type: % (%%%)', articles_with_type,
                 ROUND(100.0 * articles_with_type / NULLIF(total_articles, 0), 1);
    RAISE NOTICE '  Articles with country: % (%%%)', articles_with_country,
                 ROUND(100.0 * articles_with_country / NULLIF(total_articles, 0), 1);

    IF articles_with_type < total_articles THEN
        RAISE WARNING 'Some articles missing content_type! Check backfill logic.';
    END IF;
END $$;

COMMIT;

-- ============================================================================
-- ROLLBACK SCRIPT (if needed)
-- ============================================================================

/*
BEGIN;

DROP VIEW IF EXISTS content_type_summary;
DROP INDEX IF EXISTS idx_articles_content_type;
DROP INDEX IF EXISTS idx_articles_country;
DROP INDEX IF EXISTS idx_articles_site_content_type;

ALTER TABLE articles DROP COLUMN IF EXISTS content_type;
ALTER TABLE articles DROP COLUMN IF EXISTS country;
ALTER TABLE articles DROP COLUMN IF EXISTS new_slug;

COMMIT;
*/
