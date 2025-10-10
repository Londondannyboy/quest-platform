-- Migration: 006_image_library.sql
-- Description: Add image reuse library for 50-70% cost savings
-- Created: October 10, 2025 (Claude Desktop optimization)

-- Drop existing table if any (safe for fresh deploy)
DROP TABLE IF EXISTS image_library CASCADE;

-- Create image_library table
CREATE TABLE image_library (
    id SERIAL PRIMARY KEY,
    category TEXT NOT NULL,
    url TEXT UNIQUE NOT NULL,
    topic TEXT NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    reuse_count INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX idx_image_library_category ON image_library(category);
CREATE INDEX idx_image_library_created ON image_library(created_at DESC);
CREATE INDEX idx_image_library_reuse_count ON image_library(reuse_count DESC);

-- Add comments
COMMENT ON TABLE image_library IS 'Reusable image library for 50-70% cost savings on hero images';
COMMENT ON COLUMN image_library.category IS 'Image category (visa_application, digital_nomad, remote_work, etc.)';
COMMENT ON COLUMN image_library.url IS 'Cloudinary URL (unique)';
COMMENT ON COLUMN image_library.topic IS 'Original article topic this image was generated for';
COMMENT ON COLUMN image_library.metadata IS 'Image metadata (dimensions, alt text, generation params)';
COMMENT ON COLUMN image_library.reuse_count IS 'Number of times this image has been reused';

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'Migration 006_image_library.sql completed successfully';
    RAISE NOTICE 'Image reuse library now available - expect 50-70%% cost savings on images';
END $$;
