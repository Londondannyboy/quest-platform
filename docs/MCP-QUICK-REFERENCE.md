# MCP Quick Reference Card

**Quest Platform Development Tools**
**Version:** 2.4.0

---

## 🚀 MCP Servers Installed

| MCP | Purpose | Usage |
|-----|---------|-------|
| **GitHub Spec Kit** | Specification-driven development | `"Use GitHub Spec Kit to create spec for [feature]"` |
| **Context7** | Up-to-date library docs | `"Use Context7 to pull FastAPI docs for [topic]"` |
| **Taskmaster AI** | Task management | `"Use Taskmaster to create task: [description]"` |

---

## 📋 Common Commands

### **GitHub Spec Kit**
```
"Use GitHub Spec Kit to create a specification for user authentication"
"Generate implementation plan from spec"
"Validate code against specification"
"Update spec with new requirements"
```

### **Context7**
```
"Use Context7 to pull latest FastAPI documentation for async endpoints"
"Check Anthropic SDK docs for streaming responses"
"Find PostgreSQL best practices for connection pooling"
"Get BullMQ queue configuration examples"
```

### **Taskmaster AI**
```
"Use Taskmaster to create task: Fix authentication bug in ResearchAgent"
"List all high-priority tasks"
"Mark task #123 as completed"
"Create task from this bug report"
"Show tasks assigned to me"
```

---

## 🔒 Security Scanning

### **Run Semgrep Locally**
```bash
# Quick scan
semgrep --config .semgrep.yml backend/

# Full scan with all rulesets
semgrep --config=p/python --config=p/security-audit backend/

# Auto-fix issues
semgrep --config .semgrep.yml --autofix backend/

# JSON output
semgrep --config .semgrep.yml backend/ --json > scan.json
```

### **Check Security in CI/CD**
```bash
# View workflow runs
gh workflow list

# View specific run
gh run view --workflow=semgrep.yml

# Re-run failed workflow
gh run rerun [RUN_ID]
```

---

## 📊 GitHub Projects

### **Issue Management**
```bash
# Create issue
gh issue create --title "Bug: [description]" --label bug

# List issues
gh issue list --label bug --state open

# Assign issue
gh issue edit [NUMBER] --add-assignee @me

# Close issue
gh issue close [NUMBER]
```

### **Project Management**
```bash
# List projects
gh project list --owner Londondannyboy

# Add issue to project
gh project item-add [PROJECT_ID] --owner Londondannyboy --url [ISSUE_URL]

# View project
gh project view [PROJECT_ID] --owner Londondannyboy
```

---

## 🛠️ Development Workflow

### **1. Start New Feature**
```
1. "Use GitHub Spec Kit to create spec for: [feature name]"
2. "Use Taskmaster to create task from this spec"
3. "Use Context7 to pull [library] docs for [topic]"
4. Develop feature
5. Run: semgrep --config .semgrep.yml backend/
6. Create PR: gh pr create
7. "Use Taskmaster to mark task complete"
```

### **2. Fix Bug**
```
1. gh issue create --title "Bug: [description]" --label bug
2. git checkout -b fix/issue-[NUMBER]
3. "Use Context7 to find [library] error handling patterns"
4. Fix bug
5. Run: semgrep --config .semgrep.yml backend/
6. gh pr create --title "Fix: [description]" --body "Fixes #[NUMBER]"
```

### **3. Research Best Practices**
```
"Use Context7 to pull latest FastAPI best practices for:
- Async/await patterns
- Dependency injection
- Error handling
- Testing strategies"
```

---

## 🐛 Troubleshooting

### **MCP Not Working**
```bash
# 1. Check config
cat ~/Library/Application\ Support/Claude/claude_desktop_config.json | jq .

# 2. Verify installation
npm list -g @github/spec-kit
npm list -g @upstash/context7-mcp
npm list -g task-master-ai

# 3. Restart Claude Desktop (Cmd+Q, reopen)

# 4. Check logs
tail -f ~/Library/Logs/Claude/mcp*.log
```

### **Semgrep Issues**
```bash
# Update Semgrep
pip3 install --upgrade semgrep

# Check version
semgrep --version

# Validate config
semgrep --validate --config .semgrep.yml

# Ignore false positives
# Add to .semgrep.yml:
# options:
#   paths:
#     exclude:
#       - tests/
#       - migrations/
```

### **GitHub CLI Issues**
```bash
# Check auth status
gh auth status

# Re-authenticate
gh auth login

# Check permissions
gh auth refresh -s repo,workflow,write:packages
```

---

## 📚 Documentation

- **Full Setup:** [docs/DEVELOPMENT-SETUP.md](./DEVELOPMENT-SETUP.md)
- **Architecture:** [docs/ARCHITECTURE.md](./ARCHITECTURE.md)
- **Security Policy:** [SECURITY.md](../SECURITY.md)
- **Contributing:** [CONTRIBUTING.md](../CONTRIBUTING.md)

---

## 🔗 Quick Links

- **GitHub Spec Kit:** https://github.com/github/spec-kit
- **Context7:** https://github.com/upstash/context7
- **Taskmaster AI:** https://github.com/eyaltoledano/claude-task-master
- **Semgrep Rules:** https://semgrep.dev/explore
- **GitHub Projects:** https://github.com/Londondannyboy/quest-platform/projects

---

**Keep this reference handy during development!** 📌
