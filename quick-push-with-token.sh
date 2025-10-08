#!/bin/bash
#
# Quick Push to GitHub with Personal Access Token
# Usage: ./quick-push-with-token.sh
#

set -e  # Exit on error

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║   Quest Architecture - Quick Push with Token                  ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check if git is initialized
if [ ! -d .git ]; then
    echo "❌ Not a git repository. Run this from the quest-architecture folder."
    exit 1
fi

echo "📋 Prerequisites Checklist:"
echo ""
echo "1. ✅ You have a GitHub account"
echo "2. ⬜ You've created a Personal Access Token with 'repo' scope"
echo "3. ⬜ You've created an empty repository on GitHub named 'quest-architecture'"
echo ""
echo "Need help? See GITHUB_TOKEN_GUIDE.md for detailed instructions."
echo ""

read -p "Have you completed all prerequisites? (yes/no): " ready

if [ "$ready" != "yes" ] && [ "$ready" != "y" ]; then
    echo ""
    echo "📚 Quick Setup Instructions:"
    echo ""
    echo "1. Create Personal Access Token:"
    echo "   → Visit: https://github.com/settings/tokens"
    echo "   → Click: 'Generate new token (classic)'"
    echo "   → Name: 'Quest Architecture'"
    echo "   → Select scopes: ✅ repo, ✅ workflow"
    echo "   → Click: 'Generate token'"
    echo "   → Copy the token (starts with 'ghp_')"
    echo ""
    echo "2. Create GitHub Repository:"
    echo "   → Visit: https://github.com/new"
    echo "   → Repository name: quest-architecture"
    echo "   → Description: Multi-Site Content Intelligence Platform"
    echo "   → Choose: Public or Private"
    echo "   → ⚠️  DO NOT check 'Initialize with README'"
    echo "   → Click: 'Create repository'"
    echo ""
    echo "Run this script again when you're ready!"
    exit 0
fi

echo ""
echo "🔐 Enter Your GitHub Credentials:"
echo ""

read -p "GitHub username: " username

if [ -z "$username" ]; then
    echo "❌ Username cannot be empty"
    exit 1
fi

read -p "Repository name [quest-architecture]: " repo_name
repo_name=${repo_name:-quest-architecture}

echo ""
echo "⚠️  Your token will be hidden as you type"
read -sp "GitHub Personal Access Token: " token
echo ""

if [ -z "$token" ]; then
    echo "❌ Token cannot be empty"
    exit 1
fi

# Validate token format
if [[ ! "$token" =~ ^ghp_[a-zA-Z0-9]{36}$ ]] && [[ ! "$token" =~ ^github_pat_[a-zA-Z0-9_]{82}$ ]]; then
    echo "⚠️  Warning: Token format looks unusual. GitHub tokens typically start with 'ghp_' or 'github_pat_'"
    read -p "Continue anyway? (yes/no): " continue_anyway
    if [ "$continue_anyway" != "yes" ] && [ "$continue_anyway" != "y" ]; then
        exit 1
    fi
fi

echo ""
echo "🚀 Pushing to GitHub..."
echo ""

# Check if remote already exists
if git remote get-url origin >/dev/null 2>&1; then
    echo "📝 Remote 'origin' already exists. Updating URL..."
    git remote set-url origin "https://${token}@github.com/${username}/${repo_name}.git"
else
    echo "📝 Adding remote 'origin'..."
    git remote add origin "https://${token}@github.com/${username}/${repo_name}.git"
fi

# Push to GitHub
echo "📤 Pushing commits..."
if git push -u origin main 2>&1 | tee /tmp/push-output.txt; then
    echo ""
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║                  ✅ SUCCESS!                                   ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo ""
    echo "🎉 Your Quest Architecture is now on GitHub!"
    echo ""
    echo "📍 Repository URL:"
    echo "   https://github.com/${username}/${repo_name}"
    echo ""
    echo "🔒 Security Recommendation:"
    echo "   Remove token from remote URL for security:"
    echo "   git remote set-url origin https://github.com/${username}/${repo_name}.git"
    echo ""
    echo "📋 Next Steps:"
    echo "   1. Visit your repository on GitHub"
    echo "   2. Follow SETUP_GUIDE.md for configuration"
    echo "   3. Add secrets for CI/CD (Settings → Secrets)"
    echo "   4. Set up branch protection"
    echo "   5. Invite collaborators"
    echo ""
    echo "📚 Documentation:"
    echo "   - SETUP_GUIDE.md - GitHub configuration"
    echo "   - docs/QUICK_START.md - Local development"
    echo "   - docs/ARCHITECTURE.md - Full technical spec"
    echo ""
else
    echo ""
    echo "╔════════════════════════════════════════════════════════════════╗"
    echo "║                  ❌ PUSH FAILED                                ║"
    echo "╚════════════════════════════════════════════════════════════════╝"
    echo ""
    echo "Common Issues and Solutions:"
    echo ""
    echo "1. 'Authentication failed' or 'invalid credentials':"
    echo "   → Token is incorrect or expired"
    echo "   → Generate a new token at: https://github.com/settings/tokens"
    echo ""
    echo "2. 'Repository not found':"
    echo "   → Make sure you created the repository on GitHub first"
    echo "   → Check username and repository name spelling"
    echo "   → Verify repository exists at: https://github.com/${username}/${repo_name}"
    echo ""
    echo "3. 'Permission denied' or 'forbidden':"
    echo "   → Token needs 'repo' scope selected"
    echo "   → Regenerate token with correct scopes"
    echo ""
    echo "4. 'Updates were rejected':"
    echo "   → Repository already has content"
    echo "   → You may need to pull first: git pull origin main --allow-unrelated-histories"
    echo ""
    echo "📖 For detailed help, see:"
    echo "   - GITHUB_TOKEN_GUIDE.md"
    echo "   - DEPLOY_TO_GITHUB.md"
    echo ""
    
    # Show last few lines of error
    echo "🔍 Error details:"
    tail -n 5 /tmp/push-output.txt
    
    exit 1
fi

# Clean up
rm -f /tmp/push-output.txt

# Offer to clean up token from URL
echo ""
read -p "Remove token from git remote URL now? (recommended: yes): " cleanup
if [ "$cleanup" = "yes" ] || [ "$cleanup" = "y" ] || [ -z "$cleanup" ]; then
    git remote set-url origin "https://github.com/${username}/${repo_name}.git"
    echo "✅ Token removed from remote URL"
    echo ""
    echo "ℹ️  For future pushes, you can:"
    echo "   - Use 'gh auth login' (GitHub CLI)"
    echo "   - Set up SSH keys"
    echo "   - Use git credential helper"
fi

echo ""
echo "════════════════════════════════════════════════════════════════"
echo "🎊 Happy coding! Your Quest Architecture is live on GitHub!"
echo "════════════════════════════════════════════════════════════════"
