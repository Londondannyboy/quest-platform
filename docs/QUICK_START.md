# Quick Start Guide

Get Quest Architecture up and running in 30 minutes.

## Prerequisites

Before you begin, ensure you have:

- ✅ Python 3.11 or higher
- ✅ Node.js 18 or higher
- ✅ Docker and Docker Compose
- ✅ Git
- ✅ PostgreSQL client tools (psql)

## 🚀 Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/quest-architecture.git
cd quest-architecture
```

### 2. Set Up Backend

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Set Up Frontend

```bash
cd ../frontend/relocation.quest

# Install dependencies
npm install

# Repeat for other sites
cd ../placement.quest && npm install
cd ../rainmaker.quest && npm install
```

### 4. Configure Environment Variables

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your values
nano .env
```

**Required Environment Variables:**

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/quest_dev

# Redis
REDIS_URL=redis://localhost:6379

# AI APIs
PERPLEXITY_API_KEY=your_perplexity_key
ANTHROPIC_API_KEY=your_anthropic_key
OPENAI_API_KEY=your_openai_key
REPLICATE_API_TOKEN=your_replicate_token

# Directus
DIRECTUS_URL=http://localhost:8055
DIRECTUS_API_TOKEN=your_directus_token
```

### 5. Start Local Services

```bash
# Start PostgreSQL and Redis with Docker
docker-compose up -d

# Verify services are running
docker-compose ps
```

### 6. Initialize Database

```bash
cd backend

# Run migrations
psql $DATABASE_URL -f migrations/001_initial_schema.sql
psql $DATABASE_URL -f migrations/002_create_users.sql

# Verify schema
psql $DATABASE_URL -c "\dt"
```

### 7. Start Development Servers

**Backend API:**

```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

**Workers:**

```bash
cd backend
source venv/bin/activate
python -m app.workers.main
```

**Directus CMS:**

```bash
docker-compose up directus
```

**Frontend:**

```bash
cd frontend/relocation.quest
npm run dev
```

### 8. Verify Installation

Open your browser and check:

- ✅ API: http://localhost:8000/docs (FastAPI Swagger UI)
- ✅ Directus: http://localhost:8055 (CMS admin)
- ✅ Frontend: http://localhost:4321 (Astro dev server)

## 🧪 Test the System

### Generate Your First Article

```bash
# Using curl
curl -X POST http://localhost:8000/api/articles/generate \
  -H "Content-Type: application/json" \
  -d '{
    "topic": "Best cities for digital nomads in 2025",
    "target_site": "relocation",
    "priority": 5
  }'

# Response
{
  "job_id": "abc123",
  "status": "queued"
}
```

### Check Job Status

```bash
curl http://localhost:8000/api/articles/status/abc123

# Response
{
  "job_id": "abc123",
  "status": "completed",
  "progress": 100,
  "result_url": "http://localhost:8055/items/articles/xyz789"
}
```

### View in Directus

1. Go to http://localhost:8055
2. Login with admin credentials
3. Navigate to "Articles" collection
4. View your generated article

## 🔍 Troubleshooting

### Common Issues

**Issue:** Database connection fails

```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check connection
psql $DATABASE_URL -c "SELECT 1"
```

**Issue:** Redis connection fails

```bash
# Check Redis is running
docker-compose ps redis

# Test connection
redis-cli -u $REDIS_URL ping
```

**Issue:** Worker not processing jobs

```bash
# Check worker logs
docker-compose logs -f workers

# Check queue depth
redis-cli -u $REDIS_URL LLEN bull:articles:wait
```

**Issue:** Frontend build fails

```bash
# Clear node_modules
rm -rf node_modules package-lock.json
npm install

# Clear Astro cache
rm -rf .astro
```

## 📚 Next Steps

Now that you have Quest running locally:

1. **Explore the API:** http://localhost:8000/docs
2. **Read the Architecture:** [Full Documentation](./ARCHITECTURE.md)
3. **Understand the AI Pipeline:** [AI Agents Guide](./docs/AI_AGENTS.md)
4. **Configure Directus:** [CMS Setup Guide](./docs/DIRECTUS_SETUP.md)
5. **Deploy to Production:** [Deployment Guide](./docs/DEPLOYMENT.md)

## 🆘 Getting Help

Need assistance?

- 📖 Check the [Full Documentation](./ARCHITECTURE.md)
- 🐛 Search [GitHub Issues](https://github.com/quest/issues)
- 💬 Ask in [Discord](https://discord.gg/quest)
- 📧 Email: support@quest.example.com

## 🎉 You're Ready!

Congratulations! You now have Quest Architecture running locally. Start building amazing content with AI! 🚀
