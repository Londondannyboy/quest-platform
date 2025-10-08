# GitHub Setup Guide for Quest Architecture

This guide will help you set up the Quest Architecture repository on GitHub from scratch.

## 🚀 Step 1: Create GitHub Repository

### Option A: Via GitHub Web Interface

1. Go to https://github.com/new
2. Fill in the details:
   - **Repository name**: `quest-architecture`
   - **Description**: Multi-Site Content Intelligence Platform with AI-Assisted Production
   - **Visibility**: Public or Private (your choice)
   - **Initialize**: ❌ Don't initialize with README (we have our own)
3. Click "Create repository"

### Option B: Via GitHub CLI

```bash
gh repo create quest-architecture \
  --description "Multi-Site Content Intelligence Platform with AI-Assisted Production" \
  --public  # or --private
```

## 📦 Step 2: Push Your Local Repository

```bash
# Navigate to your repository
cd quest-architecture

# Initialize git if not already done
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Quest Architecture v2.2

- Complete architecture documentation
- Backend and frontend structure
- CI/CD pipeline with GitHub Actions
- Docker Compose for local development
- Comprehensive contribution guidelines"

# Add remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/quest-architecture.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## 🔧 Step 3: Configure GitHub Repository Settings

### Repository Settings

Go to Settings → General:

1. **Features**:
   - ✅ Issues
   - ✅ Discussions (optional but recommended)
   - ✅ Projects
   - ✅ Wiki (optional)

2. **Pull Requests**:
   - ✅ Allow squash merging
   - ✅ Always suggest updating pull request branches
   - ✅ Automatically delete head branches

3. **Merge Button**:
   - ✅ Allow merge commits
   - ✅ Allow squash merging
   - ❌ Allow rebase merging (optional)

### Branch Protection

Go to Settings → Branches → Add rule:

**Branch name pattern**: `main`

**Protect matching branches**:
- ✅ Require a pull request before merging
  - Required approvals: 1
- ✅ Require status checks to pass before merging
  - ✅ backend-tests
  - ✅ frontend-tests
  - ✅ security-scan
- ✅ Require conversation resolution before merging
- ✅ Do not allow bypassing the above settings
- ✅ Require linear history

**Rules applied to everyone**:
- ✅ Restrict pushes that create matching branches

### Add Same Rule for `develop` Branch

Repeat the above for `develop` branch but with:
- Required approvals: 0 (can be merged without approval)
- Status checks still required

## 🔐 Step 4: Add Secrets

Go to Settings → Secrets and variables → Actions:

### Required Secrets

```yaml
# Railway
RAILWAY_STAGING_TOKEN: <your-railway-staging-token>
RAILWAY_PRODUCTION_TOKEN: <your-railway-production-token>

# Vercel
VERCEL_TOKEN: <your-vercel-token>
VERCEL_ORG_ID: <your-vercel-org-id>

# API Keys (for CI/CD tests)
PERPLEXITY_API_KEY: <your-perplexity-key>
ANTHROPIC_API_KEY: <your-anthropic-key>
OPENAI_API_KEY: <your-openai-key>
REPLICATE_API_TOKEN: <your-replicate-token>

# Database (for integration tests)
TEST_DATABASE_URL: <your-test-db-url>
```

## 🏷️ Step 5: Create Labels

Go to Issues → Labels → New label:

### Priority Labels
- `priority: critical` - 🔴 Red (#E11D48)
- `priority: high` - 🟠 Orange (#F97316)
- `priority: medium` - 🟡 Yellow (#EAB308)
- `priority: low` - 🟢 Green (#10B981)

### Type Labels
- `type: bug` - 🐛 Red (#DC2626)
- `type: feature` - ✨ Blue (#3B82F6)
- `type: docs` - 📚 Gray (#6B7280)
- `type: security` - 🔒 Purple (#9333EA)
- `type: performance` - ⚡ Yellow (#FBBF24)

### Component Labels
- `component: api` - Backend API
- `component: workers` - Background workers
- `component: frontend` - Astro sites
- `component: database` - Database/migrations
- `component: infrastructure` - IaC/deployment

### Status Labels
- `status: needs-review` - 👀 Yellow
- `status: in-progress` - 🚧 Blue
- `status: blocked` - 🚫 Red
- `status: ready` - ✅ Green

### Special Labels
- `good first issue` - 🌱 Good for newcomers
- `help wanted` - 🆘 Extra attention needed
- `duplicate` - 📋 Duplicate issue
- `wontfix` - ⛔ Won't be fixed

## 📊 Step 6: Set Up Project Board (Optional)

1. Go to Projects → New project
2. Choose "Board" layout
3. Name it "Quest Development"
4. Add columns:
   - 📋 Backlog
   - 🎯 Ready
   - 🚧 In Progress
   - 👀 In Review
   - ✅ Done

## 🔔 Step 7: Configure Notifications

### For Team Members

Go to Watch → Custom:
- ✅ Issues
- ✅ Pull requests
- ✅ Discussions
- ✅ Releases

### For Collaborators

Settings → Manage access → Invite collaborator:
- Add team members with appropriate permissions
- **Maintain**: For core team
- **Write**: For regular contributors
- **Read**: For read-only access

## 🎨 Step 8: Customize Repository

### About Section

Click ⚙️ next to "About":
- **Description**: Multi-Site Content Intelligence Platform with AI-Assisted Production
- **Website**: https://relocation.quest (or your domain)
- **Topics**: 
  - `ai`
  - `content-generation`
  - `fastapi`
  - `astro`
  - `postgresql`
  - `claude`
  - `perplexity`

### Social Preview Image

Settings → General → Social preview:
- Upload a banner image (1280x640px)
- Use Quest Architecture diagram or logo

## 📝 Step 9: Create Initial Issues

Create issues for your roadmap:

### Phase 1 Issues
```
Title: Set up Neon PostgreSQL database
Labels: component: database, priority: high, status: ready
Milestone: Phase 1
```

```
Title: Deploy Railway services
Labels: component: infrastructure, priority: high, status: ready
Milestone: Phase 1
```

### Create Milestones
- Phase 1: Foundation (Weeks 1-2)
- Phase 2: CMS & Frontend (Weeks 3-4)
- Phase 3: Production Hardening (Weeks 5-6)

## 🤖 Step 10: Configure GitHub Actions

The CI/CD workflow is already included in `.github/workflows/ci-cd.yml`.

### Verify Workflow

1. Go to Actions tab
2. You should see "CI/CD Pipeline" workflow
3. It will run on:
   - Every push to `main` or `develop`
   - Every pull request to `main` or `develop`

### First Run

Make a small change and push to trigger the workflow:
```bash
# Make a small change
echo "# Quest Architecture" >> README.md

# Commit and push
git add README.md
git commit -m "docs: update README"
git push origin main
```

Check Actions tab to see the workflow run.

## 📢 Step 11: Announce Your Repository

### README Badges

Add badges to your README (already included):
- Architecture Grade
- Status
- License
- Build Status (once CI/CD runs)

### Share

- Post on Twitter/X
- Share in relevant Slack/Discord communities
- Add to awesome lists if applicable
- Write a blog post about your architecture

## 🔄 Step 12: Set Up Development Branch

```bash
# Create develop branch
git checkout -b develop

# Push develop branch
git push -u origin develop

# Set develop as default branch (optional)
# Go to Settings → Branches → Default branch → Change to 'develop'
```

## ✅ Verification Checklist

- [ ] Repository created on GitHub
- [ ] Initial commit pushed
- [ ] Branch protection configured for `main` and `develop`
- [ ] Secrets added for CI/CD
- [ ] Labels created
- [ ] Project board set up (optional)
- [ ] Team members invited
- [ ] About section filled
- [ ] Initial issues created
- [ ] GitHub Actions workflow running
- [ ] Development branch created

## 🎉 You're All Set!

Your Quest Architecture repository is now fully configured on GitHub!

### Next Steps

1. ✅ Complete local development setup (see QUICK_START.md)
2. ✅ Start working on Phase 1 tasks
3. ✅ Create your first pull request
4. ✅ Deploy to staging environment

## 📚 Additional Resources

- [GitHub Docs](https://docs.github.com)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Branch Protection Rules](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/defining-the-mergeability-of-pull-requests/about-protected-branches)
- [GitHub Project Boards](https://docs.github.com/en/issues/organizing-your-work-with-project-boards)

## 🆘 Troubleshooting

### CI/CD Not Running

- Check GitHub Actions are enabled: Settings → Actions → General
- Verify workflow file syntax
- Check secrets are configured

### Cannot Push to Protected Branch

- Create a feature branch instead
- Submit a pull request
- Get required approvals

### Build Failing

- Check workflow logs in Actions tab
- Verify all secrets are configured
- Test locally first

---

**Need Help?** 
- 📖 Read the [Full Documentation](./docs/ARCHITECTURE.md)
- 💬 Ask in [Discussions](https://github.com/YOUR_USERNAME/quest-architecture/discussions)
- 📧 Email: support@quest.example.com

**Last Updated**: October 7, 2025
