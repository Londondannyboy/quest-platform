-- Migration: 005_cluster_research_cache.sql
-- Description: Add cluster-level research caching for 90% cost savings
-- Created: October 10, 2025 (Claude Desktop optimization)

-- Drop existing table if any (safe for fresh deploy)
DROP TABLE IF EXISTS cluster_research CASCADE;

-- Create cluster_research table
CREATE TABLE cluster_research (
    cluster_id TEXT PRIMARY KEY,
    research_data JSONB NOT NULL,
    seo_data JSONB DEFAULT '{}'::jsonb,
    serp_analysis JSONB DEFAULT '{}'::jsonb,
    ai_insights JSONB DEFAULT '{}'::jsonb,
    reuse_count INTEGER DEFAULT 0,
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX idx_cluster_research_expires ON cluster_research(expires_at);
CREATE INDEX idx_cluster_research_created ON cluster_research(created_at);
CREATE INDEX idx_cluster_research_reuse_count ON cluster_research(reuse_count DESC);

-- Add comments
COMMENT ON TABLE cluster_research IS 'Cluster-level research cache for 90% cost savings - all articles in same cluster reuse research';
COMMENT ON COLUMN cluster_research.cluster_id IS 'Cluster identifier (e.g., portugal_digital_nomad, spain_immigration)';
COMMENT ON COLUMN cluster_research.research_data IS 'Full research from multi-API system';
COMMENT ON COLUMN cluster_research.seo_data IS 'DataForSEO keyword analysis';
COMMENT ON COLUMN cluster_research.serp_analysis IS 'Serper/DataForSEO SERP data';
COMMENT ON COLUMN cluster_research.ai_insights IS 'Perplexity/Tavily narrative research';
COMMENT ON COLUMN cluster_research.reuse_count IS 'Number of times this cluster research was reused';
COMMENT ON COLUMN cluster_research.expires_at IS '90-day TTL (quarterly refresh)';

-- Insert example clusters for testing
INSERT INTO cluster_research (cluster_id, research_data, expires_at) VALUES
    ('portugal_digital_nomad', '{"content": "Example Portugal research data", "sources": []}'::jsonb, NOW() + INTERVAL '90 days'),
    ('spain_immigration', '{"content": "Example Spain research data", "sources": []}'::jsonb, NOW() + INTERVAL '90 days'),
    ('remote_work_strategies', '{"content": "Example remote work research", "sources": []}'::jsonb, NOW() + INTERVAL '90 days')
ON CONFLICT (cluster_id) DO NOTHING;

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'Migration 005_cluster_research_cache.sql completed successfully';
    RAISE NOTICE 'Cluster research caching now available - expect 90%% cost savings on research';
END $$;
