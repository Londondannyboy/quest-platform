# Using GitHub Personal Access Token (PAT)

## 🔐 Step-by-Step Guide to Push with Token

### Step 1: Create a Personal Access Token

1. **Go to GitHub Settings**:
   - Click your profile picture → Settings
   - Or go directly to: https://github.com/settings/tokens

2. **Navigate to Developer Settings**:
   - Scroll down to "Developer settings" (left sidebar)
   - Click "Personal access tokens" → "Tokens (classic)"

3. **Generate New Token**:
   - Click "Generate new token" → "Generate new token (classic)"
   - Note: Give it a descriptive name like "Quest Architecture Deployment"

4. **Configure Token Permissions**:
   Select these scopes:
   ```
   ✅ repo (Full control of private repositories)
      ✅ repo:status
      ✅ repo_deployment
      ✅ public_repo
      ✅ repo:invite
   ✅ workflow (Update GitHub Action workflows)
   ✅ write:packages (optional, for Docker images)
   ✅ delete_repo (optional, if you need to delete)
   ```

5. **Set Expiration**:
   - Choose: 90 days, 1 year, or No expiration
   - Recommendation: 90 days for security

6. **Generate and SAVE the token**:
   - Click "Generate token"
   - ⚠️ **IMPORTANT**: Copy the token NOW! You won't see it again!
   - Save it somewhere secure (password manager)

### Step 2: Create Repository on GitHub

Before pushing, create an empty repository:

1. Go to: https://github.com/new
2. Repository name: `quest-architecture`
3. Description: `Multi-Site Content Intelligence Platform with AI-Assisted Production`
4. Choose Public or Private
5. ⚠️ **DO NOT** check "Initialize with README"
6. Click "Create repository"

### Step 3: Push Using Your Token

Now you have two ways to use your token:

#### Method A: Token in Remote URL (Simple)

```bash
cd /path/to/quest-architecture

# Add remote with token embedded
git remote add origin https://YOUR_TOKEN@github.com/YOUR_USERNAME/quest-architecture.git

# Push
git push -u origin main
```

**Replace**:
- `YOUR_TOKEN` with the token you copied
- `YOUR_USERNAME` with your GitHub username

**Example**:
```bash
git remote add origin https://ghp_1234567890abcdefghijklmnop@github.com/johndoe/quest-architecture.git
git push -u origin main
```

#### Method B: Git Credential Helper (Recommended, More Secure)

```bash
cd /path/to/quest-architecture

# Configure git to use credential helper
git config --global credential.helper store

# Add remote (without token in URL)
git remote add origin https://github.com/YOUR_USERNAME/quest-architecture.git

# Push (you'll be prompted once)
git push -u origin main
```

When prompted:
- **Username**: Your GitHub username
- **Password**: Paste your token (NOT your GitHub password)

The credential helper will save this, so you won't need to enter it again.

#### Method C: Environment Variable (Most Secure)

```bash
# Set token as environment variable
export GITHUB_TOKEN="ghp_your_token_here"

# Add remote
git remote add origin https://${GITHUB_TOKEN}@github.com/YOUR_USERNAME/quest-architecture.git

# Push
git push -u origin main
```

### Step 4: Verify Push Success

After pushing, you should see:
```
Enumerating objects: 20, done.
Counting objects: 100% (20/20), done.
Delta compression using up to 8 threads
Compressing objects: 100% (18/18), done.
Writing objects: 100% (20/20), 242 KiB | 24.2 MiB/s, done.
Total 20 (delta 0), reused 0 (delta 0), pack-reused 0
To https://github.com/YOUR_USERNAME/quest-architecture.git
 * [new branch]      main -> main
Branch 'main' set up to track remote branch 'main' from 'origin'.
```

### Step 5: View Your Repository

Visit: `https://github.com/YOUR_USERNAME/quest-architecture`

You should see:
- ✅ All 18 files
- ✅ Beautiful README with badges
- ✅ 2 commits
- ✅ GitHub Actions workflow ready

## 🔒 Security Best Practices

### DO ✅
- Store token in password manager
- Use credential helper to avoid exposing token
- Set expiration dates on tokens
- Use fine-grained tokens when possible
- Revoke tokens when done or if compromised

### DON'T ❌
- Commit tokens to git repositories
- Share tokens with others
- Use tokens in public URLs
- Leave tokens in command history
- Use the same token for everything

## 🧹 Cleanup After Push

After successful push, you can remove the token from git config:

```bash
# If you used credential.helper store
git config --global --unset credential.helper

# Remove credential file
rm ~/.git-credentials

# Or just use a clean remote URL
git remote set-url origin https://github.com/YOUR_USERNAME/quest-architecture.git
```

## 🔄 Alternative: Use GitHub CLI (No Token Needed)

If you have GitHub CLI installed:

```bash
# Login once (browser authentication)
gh auth login

# Create and push repository
gh repo create quest-architecture --public --source=. --push
```

This is easier and more secure than managing tokens!

## ❓ Troubleshooting

### "Authentication failed"
→ Double-check your token and username
→ Ensure token has `repo` scope
→ Check if token expired

### "Repository not found"
→ Make sure you created the repo on GitHub first
→ Check repository name spelling
→ Verify your username

### "Permission denied"
→ Token needs `repo` scope
→ Check if you're using the right token
→ Try regenerating the token

## 📋 Quick Reference

**Token Format**: `ghp_` followed by alphanumeric characters

**Minimum Required Scopes**:
- `repo` - For pushing code
- `workflow` - For GitHub Actions

**Remote URL Format**:
```
https://TOKEN@github.com/USERNAME/REPO.git
```

## 🎯 Next Steps After Pushing

1. ✅ Go to your GitHub repository
2. ✅ Follow SETUP_GUIDE.md for configuration
3. ✅ Add secrets for CI/CD
4. ✅ Set up branch protection
5. ✅ Invite collaborators

---

**Need Help?**
- GitHub Docs: https://docs.github.com/en/authentication
- Token Settings: https://github.com/settings/tokens
- GitHub CLI: https://cli.github.com/

**Security Issue?**
- Revoke immediately: https://github.com/settings/tokens
- Generate new token
- Update git remote URL
