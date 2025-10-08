# Contributing to Quest Architecture

First off, thank you for considering contributing to Quest! It's people like you that make Quest such a great platform.

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Commit Messages](#commit-messages)
- [Pull Request Process](#pull-request-process)
- [Architecture Decisions](#architecture-decisions)

## 🤝 Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code.

### Our Standards

- Be respectful and inclusive
- Accept constructive criticism gracefully
- Focus on what is best for the community
- Show empathy towards other community members

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- Git
- PostgreSQL client tools

### Setting Up Your Development Environment

1. **Fork the repository** on GitHub

2. **Clone your fork:**
   ```bash
   git clone https://github.com/YOUR_USERNAME/quest-architecture.git
   cd quest-architecture
   ```

3. **Add upstream remote:**
   ```bash
   git remote add upstream https://github.com/original/quest-architecture.git
   ```

4. **Set up backend:**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   pip install -r requirements-dev.txt
   ```

5. **Set up frontend:**
   ```bash
   cd frontend/relocation.quest
   npm install
   ```

6. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your development API keys
   ```

7. **Start services:**
   ```bash
   docker-compose up -d
   ```

## 🔄 Development Workflow

### Branching Strategy

We use a modified Git Flow:

- `main` - Production-ready code
- `develop` - Integration branch for features
- `feature/*` - New features
- `bugfix/*` - Bug fixes
- `hotfix/*` - Emergency production fixes
- `release/*` - Release preparation

### Creating a Feature Branch

```bash
git checkout develop
git pull upstream develop
git checkout -b feature/your-feature-name
```

### Keeping Your Branch Updated

```bash
git checkout develop
git pull upstream develop
git checkout feature/your-feature-name
git rebase develop
```

## 💻 Coding Standards

### Python (Backend)

We use:
- **Black** for code formatting
- **Ruff** for linting
- **MyPy** for type checking

```bash
# Format code
black .

# Lint
ruff check .

# Type check
mypy app/
```

**Style Guidelines:**
- Maximum line length: 88 characters (Black default)
- Use type hints for all function parameters and returns
- Follow PEP 8
- Write docstrings for all public functions

**Example:**
```python
from typing import List, Optional

async def generate_article(
    topic: str,
    target_site: str,
    priority: Optional[int] = None
) -> dict:
    """
    Generate an article using the 4-agent pipeline.
    
    Args:
        topic: The article topic
        target_site: One of 'relocation', 'placement', 'rainmaker'
        priority: Optional job priority (1-10)
    
    Returns:
        dict: Article data including content, quality_score, etc.
    
    Raises:
        ValueError: If target_site is invalid
        APIError: If external API calls fail
    """
    # Implementation here
```

### TypeScript/JavaScript (Frontend)

We use:
- **ESLint** for linting
- **Prettier** for formatting

```bash
# Format code
npm run format

# Lint
npm run lint
```

**Style Guidelines:**
- Use TypeScript for new code
- Prefer functional components (React/Astro)
- Use async/await over promises
- Follow Airbnb style guide

### SQL

**Style Guidelines:**
- Use uppercase for SQL keywords
- Use snake_case for table and column names
- Always use parameterized queries
- Add comments for complex queries

**Example:**
```sql
-- Get articles with high quality scores
SELECT 
    id,
    title,
    quality_score,
    published_date
FROM articles
WHERE 
    target_site = $1
    AND status = 'published'
    AND quality_score > 85
ORDER BY published_date DESC
LIMIT $2;
```

## 🧪 Testing Guidelines

### Backend Tests

```bash
cd backend
pytest tests/
```

**Test Structure:**
```python
# tests/test_research_agent.py
import pytest
from app.agents.research import ResearchAgent

@pytest.fixture
async def research_agent():
    """Fixture for ResearchAgent instance."""
    return ResearchAgent(db_pool, openai_client, perplexity_client)

@pytest.mark.asyncio
async def test_cache_hit(research_agent):
    """Test that cache hit returns cached data."""
    topic = "Cyprus digital nomad visa"
    
    # First call - should miss cache
    result1 = await research_agent.run(topic)
    
    # Second call - should hit cache
    result2 = await research_agent.run(topic)
    
    assert result1 == result2
    assert result2['cached'] is True
```

**Coverage Requirements:**
- Overall coverage: >80%
- Critical paths: >95%
- New code: 100%

### Frontend Tests

```bash
cd frontend/relocation.quest
npm test
```

**Test Structure:**
```typescript
// tests/components/ArticleCard.test.ts
import { describe, it, expect } from 'vitest';
import { render } from '@testing-library/svelte';
import ArticleCard from '../components/ArticleCard.astro';

describe('ArticleCard', () => {
  it('renders article title', () => {
    const { getByText } = render(ArticleCard, {
      props: {
        title: 'Test Article',
        excerpt: 'Test excerpt',
        image: '/test.jpg'
      }
    });
    
    expect(getByText('Test Article')).toBeInTheDocument();
  });
});
```

### Integration Tests

```bash
docker-compose -f docker-compose.test.yml up --abort-on-container-exit
```

## 📝 Commit Messages

We follow [Conventional Commits](https://www.conventionalcommits.org/):

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `perf`: Performance improvements
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `ci`: CI/CD changes

### Examples

```
feat(research-agent): add cache warming on startup

Implement cache warming to preload frequently accessed research
topics on worker startup. This reduces cold start latency for
common queries.

Closes #123
```

```
fix(api): handle timeout errors in article generation

Add proper error handling and retry logic for LLM API timeouts.
Implements exponential backoff with max 5 retries.

Fixes #456
```

## 🔀 Pull Request Process

### Before Submitting

1. ✅ Update your branch with latest `develop`
2. ✅ Run all tests and ensure they pass
3. ✅ Run linters and formatters
4. ✅ Update documentation if needed
5. ✅ Add tests for new functionality
6. ✅ Update CHANGELOG.md

### PR Template

When you create a PR, the template will guide you through:
- Description of changes
- Type of change
- Testing performed
- Checklist of requirements

### Review Process

1. **Automated Checks:** All CI/CD checks must pass
2. **Code Review:** At least 1 approval required
3. **Testing:** Reviewer verifies tests cover changes
4. **Documentation:** Reviewer checks docs are updated
5. **Merge:** Squash and merge to develop

### After Merge

- Delete your feature branch
- Update your local repository:
  ```bash
  git checkout develop
  git pull upstream develop
  ```

## 🏗️ Architecture Decisions

### When to Create an ADR

Create an Architecture Decision Record (ADR) when:
- Choosing between significant alternatives
- Making decisions that are hard to reverse
- Decisions that affect multiple components
- Setting patterns for future development

### ADR Template

```markdown
# ADR-XXX: Title

## Status
[Proposed | Accepted | Deprecated | Superseded]

## Context
What is the issue that we're seeing that is motivating this decision?

## Decision
What is the change that we're proposing and/or doing?

## Consequences
What becomes easier or more difficult to do because of this change?

## Alternatives Considered
What other options did we evaluate?
```

### Example

See `docs/adr/0001-use-neon-launch-tier.md` for a complete example.

## 🎯 Areas Needing Contributions

### High Priority

- 🔍 Improve cache hit rate algorithms
- 📊 Enhanced monitoring dashboards
- 🔒 Additional security hardening
- 📝 More comprehensive documentation

### Good First Issues

Look for issues tagged with `good first issue` in the issue tracker. These are:
- Well-defined scope
- Clear acceptance criteria
- Suitable for newcomers
- Good learning opportunities

## 💬 Getting Help

### Communication Channels

- 💬 **Discord:** [Join our community](https://discord.gg/quest)
- 📧 **Email:** dev@quest.example.com
- 📖 **Docs:** [Full documentation](./docs/)
- 🐛 **Issues:** [GitHub Issues](https://github.com/quest/issues)

### Ask Questions

Don't hesitate to ask questions! You can:
- Comment on the issue you're working on
- Start a discussion in GitHub Discussions
- Ask in our Discord channel
- Send an email to the dev team

## 📄 License

By contributing to Quest, you agree that your contributions will be licensed under the MIT License.

## 🙏 Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Given credit in documentation

Thank you for making Quest better! 🚀
