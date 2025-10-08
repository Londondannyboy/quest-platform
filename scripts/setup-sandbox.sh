#!/bin/bash
# Quest Platform v2.2 - Sandbox Database Setup
# Sets up a local development database with example content

set -e

echo "🚀 Quest Platform - Sandbox Setup"
echo "=================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    echo -e "${RED}❌ Error: DATABASE_URL not set${NC}"
    echo "Please set DATABASE_URL environment variable"
    echo "Example: export DATABASE_URL='postgresql://user:pass@localhost:5432/quest_sandbox'"
    exit 1
fi

echo -e "${GREEN}✓${NC} DATABASE_URL found"
echo ""

# Step 1: Check database connection
echo "1️⃣  Testing database connection..."
if psql "$DATABASE_URL" -c "SELECT 1;" > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Database connection successful"
else
    echo -e "${RED}❌ Cannot connect to database${NC}"
    exit 1
fi
echo ""

# Step 2: Run initial schema migrations
echo "2️⃣  Running schema migrations..."
if [ -f "backend/migrations/001_initial_schema.sql" ]; then
    psql "$DATABASE_URL" -f backend/migrations/001_initial_schema.sql
    echo -e "${GREEN}✓${NC} Schema migrations applied"
else
    echo -e "${YELLOW}⚠${NC}  001_initial_schema.sql not found, skipping"
fi
echo ""

# Step 3: Create extensions
echo "3️⃣  Installing PostgreSQL extensions..."
psql "$DATABASE_URL" << EOF
-- Install required extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
EOF
echo -e "${GREEN}✓${NC} Extensions installed"
echo ""

# Step 4: Seed example data
echo "4️⃣  Seeding example content..."
if [ -f "backend/migrations/seed_example_data.sql" ]; then
    psql "$DATABASE_URL" -f backend/migrations/seed_example_data.sql
    echo -e "${GREEN}✓${NC} Example data seeded"
else
    echo -e "${YELLOW}⚠${NC}  seed_example_data.sql not found, skipping"
fi
echo ""

# Step 5: Verify setup
echo "5️⃣  Verifying sandbox setup..."
ARTICLE_COUNT=$(psql "$DATABASE_URL" -t -c "SELECT COUNT(*) FROM articles;")
RESEARCH_COUNT=$(psql "$DATABASE_URL" -t -c "SELECT COUNT(*) FROM article_research;")

echo "   Articles: $ARTICLE_COUNT"
echo "   Research cache entries: $RESEARCH_COUNT"
echo ""

if [ "$ARTICLE_COUNT" -gt 0 ]; then
    echo -e "${GREEN}✅ Sandbox setup complete!${NC}"
    echo ""
    echo "📊 Quick Stats:"
    psql "$DATABASE_URL" -c "
        SELECT
            target_site,
            COUNT(*) as articles,
            ROUND(AVG(quality_score)) as avg_quality,
            ROUND(AVG(word_count)) as avg_words
        FROM articles
        GROUP BY target_site
        ORDER BY target_site;
    "
    echo ""
    echo "🔗 Sample Articles:"
    psql "$DATABASE_URL" -c "
        SELECT
            slug,
            title,
            status,
            quality_score
        FROM articles
        ORDER BY created_at DESC
        LIMIT 5;
    "
    echo ""
    echo "🎉 You can now start developing!"
    echo ""
    echo "Next steps:"
    echo "  1. Start backend: cd backend && uvicorn app.main:app --reload"
    echo "  2. Start workers: cd backend && python -m app.workers.queue_worker"
    echo "  3. Start frontend: cd frontend/relocation.quest && npm run dev"
else
    echo -e "${YELLOW}⚠${NC}  Warning: No articles found. Seed data may not have loaded correctly."
fi
