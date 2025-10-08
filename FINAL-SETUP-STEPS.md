# Quest Platform - Final Setup Steps

**Status:** Ready for MCP Configuration
**Date:** October 8, 2025

---

## ✅ COMPLETED

- ✅ **Context7 MCP** installed (v1.0.20)
- ✅ **Taskmaster AI MCP** installed (v0.27.3)
- ✅ **GitHub Spec Kit** cloned (`/Users/dankeegan/spec-kit`)
- ✅ **Upstash Redis** database created
- ✅ **Credentials file** created (`/Users/dankeegan/quest-credentials.md`)
- ✅ **MCP config file** created (`/Users/dankeegan/claude-desktop-mcp-config.json`)
- ✅ **Semgrep rules** configured (`.semgrep.yml`)
- ✅ **Documentation** complete

---

## 🚀 NEXT STEPS (Your Action Required)

### **Step 1: Generate GitHub Token**

1. Go to: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select scopes:
   - ✅ repo (all)
   - ✅ workflow
   - ✅ write:packages
   - ✅ read:org
   - ✅ project
4. Generate and copy token
5. Add to `/Users/dankeegan/quest-credentials.md`

---

### **Step 2: Configure Claude Desktop**

**Option A: Copy pre-made config (Recommended)**
```bash
# Copy the config file to Claude Desktop location
cp /Users/dankeegan/claude-desktop-mcp-config.json \
   ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

**Option B: Manual configuration**
1. Open: `~/Library/Application Support/Claude/claude_desktop_config.json`
2. Copy contents from: `/Users/dankeegan/claude-desktop-mcp-config.json`
3. Save and close

**Current Config Includes:**
- ✅ Context7 (with Upstash credentials)
- ✅ Taskmaster AI (with quest-platform workspace)

**To Add Later (after getting GitHub token):**
```json
{
  "mcpServers": {
    "github-spec-kit": {
      "command": "python3",
      "args": ["/Users/dankeegan/spec-kit/src/specify.py"],
      "env": {
        "GITHUB_TOKEN": "[ADD YOUR TOKEN HERE]"
      }
    },
    "context7": {
      ... existing config ...
    },
    "taskmaster": {
      ... existing config ...
    }
  }
}
```

---

### **Step 3: Restart Claude Desktop**

```bash
# Quit Claude Desktop completely
# Press Cmd+Q

# Reopen Claude Desktop
# MCPs will load automatically
```

---

### **Step 4: Verify MCP Servers**

**In Claude Desktop:**
1. Open new conversation
2. Look for tools icon in bottom-left
3. Should see:
   - ✅ context7 tools
   - ✅ taskmaster tools
   - ⚠️  github-spec-kit (after adding GitHub token)

**Test Commands:**
```
"Use Context7 to pull latest FastAPI documentation for async endpoints"

"Use Taskmaster to list current tasks in quest-platform workspace"
```

---

### **Step 5: Create GitHub Project Board**

**Option A: Via Web (Recommended)**
1. Go to: https://github.com/Londondannyboy/quest-platform/projects
2. Click "New project"
3. Select "Board" template
4. Name: "Quest Platform Development"
5. Create columns:
   - 📋 Backlog
   - 🔍 Ready
   - 🚧 In Progress
   - ✅ Done
6. Enable automation (issues → columns)

**Option B: Via CLI (after installing gh)**
```bash
# Install GitHub CLI first
# Then:
gh project create \
  --owner Londondannyboy \
  --title "Quest Platform Development"
```

---

### **Step 6: Install Remaining Tools (Optional)**

**Semgrep (Security Scanning):**
```bash
pip3 install semgrep

# Test it
semgrep --config .semgrep.yml backend/
```

**GitHub CLI (if you want CLI access):**
```bash
# Option 1: Download from https://cli.github.com/

# Option 2: Install Homebrew first, then:
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install gh

# Authenticate
gh auth login
```

---

## 📊 Current Status

### **MCP Servers**
| Server | Status | Configuration |
|--------|--------|---------------|
| Context7 | ✅ Installed + Configured | Upstash credentials added |
| Taskmaster AI | ✅ Installed + Configured | Workspace: quest-platform |
| GitHub Spec Kit | ⚠️  Cloned, needs token | Waiting for GitHub token |

### **Credentials**
| Service | Status | Location |
|---------|--------|----------|
| Upstash Redis | ✅ Complete | `quest-credentials.md` |
| Upstash API Key | ✅ Complete | `quest-credentials.md` |
| GitHub Token | ⚠️  Needed | Generate at GitHub settings |
| Taskmaster API | ✅ Complete | Already configured |

### **Tools**
| Tool | Status | Location |
|------|--------|----------|
| Context7 | ✅ Installed | `npm list -g @upstash/context7-mcp` |
| Taskmaster AI | ✅ Installed | `npm list -g task-master-ai` |
| GitHub Spec Kit | ✅ Cloned | `/Users/dankeegan/spec-kit` |
| Semgrep | ⚠️  Config only | Run `pip3 install semgrep` |
| GitHub CLI | ⚠️  Not installed | Optional |

---

## 🎯 Priority Actions

**Do NOW:**
1. ✅ Generate GitHub token (5 minutes)
2. ✅ Copy MCP config to Claude Desktop (1 minute)
3. ✅ Restart Claude Desktop (30 seconds)
4. ✅ Test Context7 and Taskmaster (2 minutes)

**Do SOON:**
5. ⚠️  Add GitHub token to MCP config (after step 1)
6. ⚠️  Create GitHub Project board (10 minutes)
7. ⚠️  Install Semgrep for security scanning (5 minutes)

**Do LATER:**
8. ⏰ Install GitHub CLI (optional)
9. ⏰ Run initial security scan

---

## 📚 Documentation

**All credentials:** `/Users/dankeegan/quest-credentials.md`
**MCP config:** `/Users/dankeegan/claude-desktop-mcp-config.json`
**Setup guide:** `docs/DEVELOPMENT-SETUP.md`
**Quick reference:** `docs/MCP-QUICK-REFERENCE.md`

---

## 🆘 Troubleshooting

**MCPs not showing in Claude Desktop:**
```bash
# Check config file exists
ls -la ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Verify JSON syntax
cat ~/Library/Application\ Support/Claude/claude_desktop_config.json | python3 -m json.tool

# Check Claude logs
tail -f ~/Library/Logs/Claude/mcp*.log
```

**Context7 not working:**
```bash
# Test Redis connection
redis-cli --tls -u redis://default:ASjjAAIncDI5ZTQ5YTUzOTQ4ZTI0NTYwYTQxOTFmYmZiMmI3ZGY1ZnAyMTA0Njc@humorous-gibbon-10467.upstash.io:6379

# Should see: humorous-gibbon-10467.upstash.io:6379>
# Type: PING
# Should see: PONG
```

**Taskmaster AI not working:**
```bash
# Verify installation
npm list -g task-master-ai

# Should show: task-master-ai@0.27.3
```

---

## ✅ When You're Done

You should be able to use these commands in Claude Desktop:

```
"Use Context7 to pull latest Anthropic SDK documentation"
"Use Context7 to find FastAPI dependency injection examples"

"Use Taskmaster to create task: Implement user authentication"
"Use Taskmaster to list all tasks"

"Use GitHub Spec Kit to create specification for [feature]"  (after adding token)
```

---

**Ready to start delivery phase once MCPs are configured!** 🚀
