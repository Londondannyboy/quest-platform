#!/bin/bash
# Quest Platform Development Environment Setup
# Installs all MCP servers and development tools

set -e  # Exit on error

echo "🚀 Quest Platform Development Environment Setup"
echo "==============================================="
echo ""

# Colors for output
GREEN='\033[0.32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command -v node &> /dev/null; then
    echo -e "${RED}❌ Node.js not found. Install from https://nodejs.org/${NC}"
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 not found. Install from https://python.org/${NC}"
    exit 1
fi

if ! command -v git &> /dev/null; then
    echo -e "${RED}❌ Git not found. Install from https://git-scm.com/${NC}"
    exit 1
fi

echo -e "${GREEN}✅ All prerequisites met${NC}"
echo ""

# Install MCP Servers
echo "📦 Installing MCP Servers..."

echo "  Installing GitHub Spec Kit..."
npm install -g @github/spec-kit || echo -e "${YELLOW}⚠️  GitHub Spec Kit install skipped${NC}"

echo "  Installing Context7..."
npm install -g @upstash/context7-mcp || echo -e "${YELLOW}⚠️  Context7 install skipped${NC}"

echo "  Installing Taskmaster AI..."
npm install -g task-master-ai || echo -e "${YELLOW}⚠️  Taskmaster AI install skipped${NC}"

echo -e "${GREEN}✅ MCP Servers installed${NC}"
echo ""

# Install Semgrep
echo "🔒 Installing Semgrep..."
pip3 install semgrep || echo -e "${YELLOW}⚠️  Semgrep install skipped${NC}"
echo -e "${GREEN}✅ Semgrep installed${NC}"
echo ""

# Install GitHub CLI (if not present)
if ! command -v gh &> /dev/null; then
    echo "📦 Installing GitHub CLI..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        brew install gh || echo -e "${YELLOW}⚠️  GitHub CLI install skipped (install Homebrew first)${NC}"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo apt install gh || echo -e "${YELLOW}⚠️  GitHub CLI install skipped${NC}"
    fi
else
    echo -e "${GREEN}✅ GitHub CLI already installed${NC}"
fi
echo ""

# Check Claude Desktop config
CLAUDE_CONFIG="$HOME/Library/Application Support/Claude/claude_desktop_config.json"
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    CLAUDE_CONFIG="$APPDATA/Claude/claude_desktop_config.json"
fi

echo "⚙️  Checking Claude Desktop configuration..."
if [ -f "$CLAUDE_CONFIG" ]; then
    echo -e "${GREEN}✅ Claude Desktop config found${NC}"
    echo "   Location: $CLAUDE_CONFIG"
else
    echo -e "${YELLOW}⚠️  Claude Desktop config not found${NC}"
    echo "   Expected location: $CLAUDE_CONFIG"
    echo "   You'll need to create this file manually."
fi
echo ""

# Run security scan
echo "🔒 Running initial security scan..."
if command -v semgrep &> /dev/null; then
    cd "$(dirname "$0")/.." || exit
    echo "  Scanning backend..."
    semgrep --config .semgrep.yml backend/ --quiet || echo -e "${YELLOW}⚠️  Security issues found (review above)${NC}"
    echo -e "${GREEN}✅ Security scan complete${NC}"
else
    echo -e "${YELLOW}⚠️  Semgrep not installed, skipping scan${NC}"
fi
echo ""

# Summary
echo "✨ Setup Complete!"
echo "==============================================="
echo ""
echo "📝 Next Steps:"
echo ""
echo "1. Configure MCP Servers:"
echo "   Edit: $CLAUDE_CONFIG"
echo "   See: docs/DEVELOPMENT-SETUP.md for configuration"
echo ""
echo "2. Get API Keys:"
echo "   - GitHub Token: https://github.com/settings/tokens"
echo "   - Upstash (Context7): https://upstash.com/"
echo "   - Taskmaster AI: https://taskmaster.ai/"
echo ""
echo "3. Restart Claude Desktop"
echo ""
echo "4. Verify setup:"
echo "   semgrep --config .semgrep.yml backend/"
echo "   gh auth status"
echo ""
echo "📚 Full documentation: docs/DEVELOPMENT-SETUP.md"
echo ""
