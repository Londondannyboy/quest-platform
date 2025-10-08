#!/bin/bash
# Quest Platform v2.2 - Local Development Setup Script
# Run: chmod +x setup.sh && ./setup.sh

set -e  # Exit on error

echo "=========================================="
echo "Quest Platform v2.2 - Setup"
echo "=========================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check prerequisites
echo "Checking prerequisites..."

command -v python3 >/dev/null 2>&1 || { echo -e "${RED}Python 3.11+ required but not installed${NC}"; exit 1; }
command -v node >/dev/null 2>&1 || { echo -e "${RED}Node.js 18+ required but not installed${NC}"; exit 1; }
command -v docker >/dev/null 2>&1 || { echo -e "${RED}Docker required but not installed${NC}"; exit 1; }
command -v psql >/dev/null 2>&1 || { echo -e "${RED}PostgreSQL client (psql) required but not installed${NC}"; exit 1; }

echo -e "${GREEN}✓ All prerequisites found${NC}"
echo ""

# Backend setup
echo "=========================================="
echo "1. Backend Setup"
echo "=========================================="

cd backend

if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Creating .env from .env.example...${NC}"
    cp .env.example .env
    echo -e "${YELLOW}⚠ Edit backend/.env with your actual API keys and database credentials${NC}"
else
    echo -e "${GREEN}✓ .env already exists${NC}"
fi

echo "Creating Python virtual environment..."
python3 -m venv venv

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo -e "${GREEN}✓ Backend setup complete${NC}"
echo ""

cd ..

# Directus setup
echo "=========================================="
echo "2. Directus Setup"
echo "=========================================="

cd directus

if [ ! -f ".env" ]; then
    echo -e "${YELLOW}Creating .env from .env.example...${NC}"
    cp .env.example .env

    # Generate random keys
    KEY=$(openssl rand -base64 32)
    SECRET=$(openssl rand -base64 32)

    # Update .env with generated keys
    sed -i.bak "s/DIRECTUS_KEY=.*/DIRECTUS_KEY=$KEY/" .env
    sed -i.bak "s/DIRECTUS_SECRET=.*/DIRECTUS_SECRET=$SECRET/" .env
    rm .env.bak

    echo -e "${GREEN}✓ Generated random DIRECTUS_KEY and DIRECTUS_SECRET${NC}"
    echo -e "${YELLOW}⚠ Edit directus/.env with your database and Cloudinary credentials${NC}"
else
    echo -e "${GREEN}✓ .env already exists${NC}"
fi

echo -e "${GREEN}✓ Directus configuration ready${NC}"
echo ""

cd ..

# Frontend setup
echo "=========================================="
echo "3. Frontend Setup (Astro Sites)"
echo "=========================================="

for site in relocation.quest placement.quest rainmaker.quest; do
    echo "Setting up $site..."

    if [ -d "frontend/$site" ]; then
        cd "frontend/$site"

        if [ ! -f "package.json" ]; then
            echo -e "${YELLOW}⚠ $site package.json not found, skipping${NC}"
        else
            echo "Installing npm dependencies..."
            npm install
            echo -e "${GREEN}✓ $site setup complete${NC}"
        fi

        cd ../..
    else
        echo -e "${YELLOW}⚠ frontend/$site directory not found${NC}"
    fi
done

echo ""

# Database setup (if DATABASE_URL is set)
echo "=========================================="
echo "4. Database Setup"
echo "=========================================="

if [ -z "$DATABASE_URL" ]; then
    echo -e "${YELLOW}⚠ DATABASE_URL not set. Skipping database migrations.${NC}"
    echo -e "${YELLOW}To run migrations later:${NC}"
    echo "  export DATABASE_URL='postgresql://...'"
    echo "  psql \$DATABASE_URL -f backend/migrations/001_initial_schema.sql"
    echo "  psql \$DATABASE_URL -f backend/migrations/002_create_users.sql"
else
    echo "DATABASE_URL found. Running migrations..."

    echo "Running 001_initial_schema.sql..."
    psql "$DATABASE_URL" -f backend/migrations/001_initial_schema.sql

    echo -e "${YELLOW}⚠ Edit backend/migrations/002_create_users.sql to set passwords${NC}"
    echo "Then run: psql \$DATABASE_URL -f backend/migrations/002_create_users.sql"

    echo -e "${GREEN}✓ Initial schema migration complete${NC}"
fi

echo ""

# Summary
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo -e "${GREEN}Next Steps:${NC}"
echo ""
echo "1. Configure environment variables:"
echo "   - Edit backend/.env (AI API keys, database, Redis)"
echo "   - Edit directus/.env (database, Cloudinary)"
echo ""
echo "2. Start Directus:"
echo "   cd directus && docker-compose up -d"
echo "   Open http://localhost:8055"
echo ""
echo "3. Start Backend API:"
echo "   cd backend"
echo "   source venv/bin/activate"
echo "   uvicorn app.main:app --reload"
echo "   Open http://localhost:8000/docs"
echo ""
echo "4. Start Frontend (any site):"
echo "   cd frontend/relocation.quest"
echo "   npm run dev"
echo "   Open http://localhost:4321"
echo ""
echo "5. Generate your first article:"
echo "   curl -X POST http://localhost:8000/api/articles/generate \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"topic\":\"Test article\",\"target_site\":\"relocation\"}'"
echo ""
echo -e "${YELLOW}For production deployment, see DEPLOYMENT.md${NC}"
echo ""
echo "Documentation:"
echo "  - README.md - Overview and quick start"
echo "  - DEPLOYMENT.md - Production deployment guide"
echo "  - docs/ - Additional documentation"
echo ""
echo -e "${GREEN}Happy building! 🚀${NC}"
