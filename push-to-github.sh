#!/bin/bash
#
# Push Quest Architecture to GitHub
# 
# This script helps you push the repository to GitHub.
# You have two options:
#

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║   Quest Architecture v2.2 - GitHub Push Helper                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check if git is configured
if ! git config --global user.name > /dev/null 2>&1; then
    echo "⚠️  Git user not configured. Setting up..."
    read -p "Enter your name: " git_name
    read -p "Enter your email: " git_email
    git config --global user.name "$git_name"
    git config --global user.email "$git_email"
    echo "✅ Git configured"
    echo ""
fi

echo "Choose how to create your GitHub repository:"
echo ""
echo "Option 1: Use GitHub CLI (gh)"
echo "  - Fastest and easiest"
echo "  - Requires: gh CLI installed and authenticated"
echo ""
echo "Option 2: Use Personal Access Token (PAT)"
echo "  - Secure and reliable"
echo "  - You create the repo on GitHub first"
echo "  - You'll need a GitHub token"
echo ""
echo "Option 3: Manual (GitHub Web + Git)"
echo "  - Works without token/gh CLI"
echo "  - Uses git credential helper"
echo ""

read -p "Which option? (1, 2, or 3): " option

if [ "$option" == "1" ]; then
    echo ""
    echo "🚀 Creating repository with GitHub CLI..."
    echo ""
    
    # Check if gh is installed
    if ! command -v gh &> /dev/null; then
        echo "❌ GitHub CLI (gh) not found!"
        echo "Install it: https://cli.github.com/"
        echo ""
        echo "Or use Option 2 instead."
        exit 1
    fi
    
    # Check if authenticated
    if ! gh auth status &> /dev/null; then
        echo "❌ Not authenticated with GitHub"
        echo "Run: gh auth login"
        exit 1
    fi
    
    read -p "Repository name (quest-architecture): " repo_name
    repo_name=${repo_name:-quest-architecture}
    
    read -p "Public or Private? (public/private): " visibility
    visibility=${visibility:-public}
    
    echo ""
    echo "Creating GitHub repository: $repo_name ($visibility)..."
    
    gh repo create "$repo_name" \
        --description "Multi-Site Content Intelligence Platform with AI-Assisted Production" \
        --$visibility \
        --source=. \
        --push
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ SUCCESS! Repository created and pushed to GitHub!"
        echo ""
        echo "View your repository:"
        gh repo view --web
    else
        echo "❌ Failed to create repository"
        exit 1
    fi
    
elif [ "$option" == "2" ]; then
    echo ""
    echo "🔐 Using Personal Access Token (PAT)..."
    echo ""
    echo "Step 1: Create a GitHub Personal Access Token"
    echo "  → Go to: https://github.com/settings/tokens"
    echo "  → Click 'Generate new token (classic)'"
    echo "  → Select scopes: repo, workflow"
    echo "  → Copy the token (you'll need it in a moment)"
    echo ""
    echo "Step 2: Create repository on GitHub"
    echo "  → Go to: https://github.com/new"
    echo "  → Name: quest-architecture"
    echo "  → ⚠️  DO NOT initialize with README"
    echo "  → Click 'Create repository'"
    echo ""
    
    read -p "Press Enter after you've created the token and repository..."
    
    echo ""
    read -p "Enter your GitHub username: " username
    read -p "Enter repository name (quest-architecture): " repo_name
    repo_name=${repo_name:-quest-architecture}
    read -sp "Paste your GitHub token (hidden): " token
    echo ""
    
    if [ -z "$token" ]; then
        echo "❌ Token cannot be empty"
        exit 1
    fi
    
    remote_url="https://${token}@github.com/$username/$repo_name.git"
    
    echo ""
    echo "Step 3: Adding remote and pushing..."
    echo ""
    
    git remote add origin "$remote_url"
    git push -u origin main
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ SUCCESS! Repository pushed to GitHub!"
        echo ""
        echo "View your repository: https://github.com/$username/$repo_name"
        echo ""
        echo "🔒 Security Note:"
        echo "Your token is in the remote URL. To remove it:"
        echo "  git remote set-url origin https://github.com/$username/$repo_name.git"
    else
        echo ""
        echo "❌ Push failed. Common issues:"
        echo "  - Invalid or expired token"
        echo "  - Token doesn't have 'repo' scope"
        echo "  - Repository already has content"
        echo "  - Wrong username/repo name"
    fi
    
elif [ "$option" == "3" ]; then
    echo ""
    echo "📝 Manual Setup Instructions:"
    echo ""
    echo "Step 1: Create repository on GitHub"
    echo "  → Go to: https://github.com/new"
    echo "  → Name: quest-architecture"
    echo "  → Description: Multi-Site Content Intelligence Platform with AI-Assisted Production"
    echo "  → Make it Public or Private"
    echo "  → ⚠️  DO NOT initialize with README, license, or .gitignore"
    echo "  → Click 'Create repository'"
    echo ""
    
    read -p "Press Enter after you've created the repository on GitHub..."
    
    echo ""
    read -p "Enter your GitHub username: " username
    read -p "Enter repository name (quest-architecture): " repo_name
    repo_name=${repo_name:-quest-architecture}
    
    remote_url="https://github.com/$username/$repo_name.git"
    
    echo ""
    echo "Step 2: Adding remote and pushing..."
    echo "Remote URL: $remote_url"
    echo ""
    
    git remote add origin "$remote_url"
    git push -u origin main
    
    if [ $? -eq 0 ]; then
        echo ""
        echo "✅ SUCCESS! Repository pushed to GitHub!"
        echo ""
        echo "View your repository: https://github.com/$username/$repo_name"
    else
        echo ""
        echo "❌ Push failed. Common issues:"
        echo "  - Wrong username/repo name"
        echo "  - Not authenticated (need to set up SSH keys or personal access token)"
        echo "  - Repository already has content"
        echo ""
        echo "Try authenticating with:"
        echo "  gh auth login"
        echo ""
        echo "Or set up SSH keys:"
        echo "  https://docs.github.com/en/authentication/connecting-to-github-with-ssh"
    fi
    
else
    echo "Invalid option. Exiting."
    exit 1
fi

echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "Next Steps:"
echo "═══════════════════════════════════════════════════════════════"
echo ""
echo "1. Configure repository settings (see SETUP_GUIDE.md)"
echo "   - Branch protection"
echo "   - Secrets (API keys)"
echo "   - Labels"
echo ""
echo "2. Start development"
echo "   - Read docs/QUICK_START.md"
echo "   - Set up local environment"
echo "   - Create your first PR"
echo ""
echo "3. Review documentation"
echo "   - docs/ARCHITECTURE.md - Full spec"
echo "   - CONTRIBUTING.md - Contribution guide"
echo "   - PROJECT_STRUCTURE.md - Code organization"
echo ""
echo "═══════════════════════════════════════════════════════════════"
echo "🎉 Your Quest Architecture is now on GitHub!"
echo "═══════════════════════════════════════════════════════════════"
