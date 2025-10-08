# Development Environment Setup

**Version:** 2.4.0
**Date:** October 8, 2025
**Purpose:** MCP Integration & Development Tools Setup
**Status:** Production Ready

---

## 🎯 Overview

This guide sets up your complete development environment including:
- **GitHub Spec Kit** - Specification-driven development
- **Context7 MCP** - Up-to-date library documentation
- **Taskmaster AI MCP** - Task management integration
- **Semgrep** - Security scanning
- **GitHub Projects** - Issue tracking

---

## 📋 Prerequisites

```bash
# Required
- Node.js 18+
- Python 3.11+
- Git
- Claude Desktop or Claude Code

# Recommended
- GitHub CLI (gh)
- Docker Desktop
```

---

## 🔧 MCP Servers Setup

### **1. GitHub Spec Kit**

**What It Does:** Specification-driven development with GitHub integration

**Installation:**
```bash
# Install GitHub Spec Kit
npm install -g @github/spec-kit

# Verify installation
spec-kit --version
```

**Configuration (Claude Desktop):**
```json
// ~/Library/Application Support/Claude/claude_desktop_config.json (Mac)
// %APPDATA%\Claude\claude_desktop_config.json (Windows)

{
  "mcpServers": {
    "github-spec-kit": {
      "command": "npx",
      "args": ["@github/spec-kit", "mcp"],
      "env": {
        "GITHUB_TOKEN": "ghp_YOUR_TOKEN_HERE"
      }
    }
  }
}
```

**Generate GitHub Token:**
```bash
# 1. Go to: https://github.com/settings/tokens
# 2. Click "Generate new token (classic)"
# 3. Select scopes:
#    - repo (all)
#    - workflow
#    - write:packages
# 4. Generate and copy token
```

**Usage in Claude:**
```
"Use GitHub Spec Kit to create a specification for [feature name]"
"Generate implementation plan from spec"
"Validate code against specification"
```

---

### **2. Context7 MCP**

**What It Does:** Always up-to-date library documentation (FastAPI, Anthropic, PostgreSQL, etc.)

**Installation:**
```bash
# Install Context7 MCP
npm install -g @upstash/context7-mcp

# Create Upstash account
# Visit: https://upstash.com/
# Create Redis database (free tier available)
```

**Configuration (Claude Desktop):**
```json
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": ["@upstash/context7-mcp"],
      "env": {
        "UPSTASH_REDIS_REST_URL": "https://your-redis-url.upstash.io",
        "UPSTASH_REDIS_REST_TOKEN": "your-token-here"
      }
    }
  }
}
```

**Get Upstash Credentials:**
```bash
# 1. Sign up: https://upstash.com/
# 2. Create Redis database
# 3. Copy REST URL and Token from dashboard
```

**Libraries to Index:**
```
- FastAPI (Python web framework)
- Anthropic SDK (Claude API)
- PostgreSQL / psycopg3 (database)
- Astro (frontend framework)
- BullMQ (job queue)
- Pydantic (data validation)
- httpx (HTTP client)
```

**Usage in Claude:**
```
"Use Context7 to pull latest FastAPI documentation for async endpoints"
"Check Anthropic SDK docs for streaming responses"
"Find PostgreSQL best practices for connection pooling"
```

---

### **3. Taskmaster AI MCP**

**What It Does:** Task management and tracking integrated with Claude

**Installation:**
```bash
# Install Taskmaster AI MCP
npm install -g task-master-ai

# Verify installation
task-master-ai --version
```

**Configuration (Claude Desktop):**
```json
{
  "mcpServers": {
    "taskmaster": {
      "command": "npx",
      "args": ["task-master-ai"],
      "env": {
        "TASKMASTER_API_KEY": "your-api-key-here",
        "TASKMASTER_WORKSPACE": "quest-platform"
      }
    }
  }
}
```

**Get Taskmaster Credentials:**
```bash
# 1. Visit: https://taskmaster.ai/ (or your Taskmaster instance)
# 2. Sign up / log in
# 3. Generate API key from settings
# 4. Create "quest-platform" workspace
```

**Usage in Claude:**
```
"Use Taskmaster to create task: Fix authentication bug in ResearchAgent"
"List all high-priority tasks"
"Mark task #123 as completed"
"Create task from this bug report"
```

---

## 🔒 Semgrep Security Scanning

**What It Does:** Automated security vulnerability scanning

**Already Configured:**
- `.semgrep.yml` - Security rules
- `.github/workflows/semgrep.yml` - GitHub Actions workflow

**Run Locally:**
```bash
# Install Semgrep
pip install semgrep

# Run security scan
semgrep --config .semgrep.yml backend/

# Run with all rulesets
semgrep --config=p/python --config=p/security-audit backend/

# Auto-fix issues (where possible)
semgrep --config .semgrep.yml --autofix backend/
```

**CI/CD Integration:**
- Runs automatically on every push/PR
- Weekly scheduled scans (Sundays 2am UTC)
- Results uploaded to GitHub Security tab
- PR comments on failures

**Review Security Findings:**
```bash
# View in GitHub
# https://github.com/Londondannyboy/quest-platform/security/code-scanning

# Or run locally and review
semgrep --config .semgrep.yml backend/ --json > scan-results.json
```

---

## 📊 GitHub Projects Setup

**What It Does:** Issue tracking, backlog management, kanban boards

**Setup Steps:**

**1. Create Project:**
```bash
# Using GitHub CLI
gh project create \
  --owner Londondannyboy \
  --title "Quest Platform Development" \
  --field Status \
  --field Priority

# Or via web:
# https://github.com/Londondannyboy/quest-platform/projects
```

**2. Configure Board:**
```
Columns:
- 📋 Backlog (priority: low, medium, high)
- 🔍 In Review (ready to start)
- 🚧 In Progress (actively working)
- ✅ Done (completed)

Labels:
- bug 🐛
- enhancement ✨
- security 🔒
- documentation 📚
- infrastructure 🏗️
```

**3. Automation:**
```yaml
# Project automation rules
- New issues → Backlog
- Assigned issues → In Progress
- Closed issues → Done
- PR opened → In Review
- PR merged → Done
```

**4. Link to Repository:**
```bash
# Link existing issues
gh project item-add PROJECT_ID --owner Londondannyboy --url ISSUE_URL

# Automatically link new issues (via templates)
```

---

## 🚀 Complete Setup Verification

### **Step 1: Verify MCP Servers**

**Claude Desktop:**
```bash
# 1. Restart Claude Desktop
# 2. Open new conversation
# 3. Check available tools in bottom-left

Expected tools:
✅ github-spec-kit
✅ context7
✅ taskmaster
```

**Test Each MCP:**
```
# Test GitHub Spec Kit
"Use GitHub Spec Kit to analyze this repository structure"

# Test Context7
"Use Context7 to pull FastAPI documentation for dependency injection"

# Test Taskmaster
"Use Taskmaster to list current tasks"
```

### **Step 2: Verify Security Scanning**

```bash
# Run Semgrep locally
cd /Users/dankeegan/quest-platform
semgrep --config .semgrep.yml backend/

# Expected: Scan completes, reports any issues
```

### **Step 3: Verify GitHub Integration**

```bash
# Check GitHub Actions
gh workflow list

# Expected workflows:
✅ CI/CD Pipeline
✅ Semgrep Security Scan
✅ Tests
✅ Lint

# Check Projects
gh project list --owner Londondannyboy
```

---

## 📝 Development Workflow

### **Starting New Feature**

```bash
# 1. Create specification
"Use GitHub Spec Kit to create spec for: [feature name]"

# 2. Create task
"Use Taskmaster to create task from this spec"

# 3. Pull relevant docs
"Use Context7 to pull [library] documentation for [topic]"

# 4. Develop feature
# (Standard development process)

# 5. Security scan
semgrep --config .semgrep.yml backend/app/

# 6. Create PR
gh pr create --title "Feature: [name]" --body "Implements [spec]"

# 7. Mark complete
"Use Taskmaster to mark task complete"
```

### **Fixing Bug**

```bash
# 1. Create issue
gh issue create --title "Bug: [description]" --label bug

# 2. Link to project
# (Automatic via GitHub automation)

# 3. Create branch
git checkout -b fix/issue-123

# 4. Pull relevant docs
"Use Context7 to find [library] error handling patterns"

# 5. Fix bug
# (Standard development)

# 6. Security scan
semgrep --config .semgrep.yml backend/

# 7. Create PR
gh pr create --title "Fix: [description]" --body "Fixes #123"

# 8. Close issue
# (Automatic when PR merged)
```

---

## 🐛 Troubleshooting

### **MCP Servers Not Showing**

**Problem:** MCPs not appearing in Claude Desktop

**Solution:**
```bash
# 1. Check config file syntax
cat ~/Library/Application\ Support/Claude/claude_desktop_config.json | jq .

# 2. Verify API keys set
# 3. Restart Claude Desktop completely (Cmd+Q, reopen)
# 4. Check Claude logs:
tail -f ~/Library/Logs/Claude/mcp*.log
```

### **Semgrep Not Running**

**Problem:** Semgrep workflow fails

**Solution:**
```bash
# 1. Check SARIF permissions
# Go to: Settings → Actions → General → Workflow permissions
# Enable: "Read and write permissions"

# 2. Re-run workflow
gh workflow run semgrep.yml

# 3. Check logs
gh run list --workflow=semgrep.yml
gh run view [RUN_ID] --log
```

### **Context7 Rate Limits**

**Problem:** "Rate limit exceeded" errors

**Solution:**
```bash
# Upgrade Upstash plan OR
# Implement caching in Claude prompts:
"Cache the FastAPI docs you just fetched and reuse for next 24 hours"
```

---

## 📚 Related Documentation

- [Architecture Guide](./ARCHITECTURE.md) - System design
- [Quick Start](./QUICK_START.md) - Get up and running
- [Security Policy](../SECURITY.md) - Vulnerability reporting
- [Contributing Guide](../CONTRIBUTING.md) - How to contribute

---

## 🔗 External Resources

**MCP Servers:**
- GitHub Spec Kit: https://github.com/github/spec-kit
- Context7: https://github.com/upstash/context7
- Taskmaster AI: https://github.com/eyaltoledano/claude-task-master

**Security:**
- Semgrep Rules: https://semgrep.dev/explore
- OWASP Top 10: https://owasp.org/www-project-top-ten/

**GitHub:**
- Projects Guide: https://docs.github.com/en/issues/planning-and-tracking-with-projects
- Actions: https://docs.github.com/en/actions

---

**Document Owner:** Platform Engineering
**Last Review:** October 8, 2025
**Next Review:** November 8, 2025
**Status:** Production Ready ✅

---

**Development environment ready. Time to build.** 🚀
