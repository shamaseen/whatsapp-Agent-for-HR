# Repository Maintenance Guide

Guide for keeping the repository clean and organized.

## 🧹 Cleanup Script

### Quick Cleanup
```bash
./scripts/cleanup.sh
```

This script removes:
- Python cache files (`__pycache__`, `*.pyc`)
- Backup files (`*.backup`, `*.bak`, `*~`)
- OS-specific files (`.DS_Store`, `Thumbs.db`)
- Temporary files (`tmp/`, `*.tmp`)
- Log files (`*.log`)
- Build artifacts (`build/`, `dist/`)
- Test cache (`.pytest_cache`)

### Manual Cleanup

**Remove Python cache:**
```bash
find . -type d -name "__pycache__" -exec rm -rf {} +
find . -type f -name "*.pyc" -delete
```

**Remove backup files:**
```bash
find . -type f -name "*.backup" -delete
find . -type f -name "*.bak" -delete
find . -type f -name "*~" -delete
```

**Remove OS files:**
```bash
find . -type f -name ".DS_Store" -delete
find . -type f -name "Thumbs.db" -delete
```

## 📁 Directory Structure

### Keep Clean
```
whatsapp_hr_assistant/
├── src/                    # Source code (keep organized)
├── tests/                  # Tests (keep updated)
├── docs/                   # Documentation (organized by category)
├── scripts/                # Utility scripts
├── .env                    # Local config (gitignored)
├── requirements.txt        # Dependencies
└── README.md              # Main documentation
```

### Avoid Committing
- `__pycache__/` - Python cache
- `*.pyc` - Bytecode files
- `token.pickle` - OAuth tokens
- `client_secret.json` - Credentials
- `.env` - Environment variables
- `*.log` - Log files
- `tmp/`, `temp/` - Temporary files

## 🔍 Check Repository Status

### Check Git Status
```bash
git status
```

### Check Ignored Files
```bash
git status --ignored
```

### Check Repository Size
```bash
du -sh .
du -sh */ | sort -hr | head -10
```

### Find Large Files
```bash
find . -type f -size +1M -exec ls -lh {} \; | sort -k5 -hr | head -10
```

## 📝 Documentation Organization

### Current Structure
```
docs/
├── DOCS_INDEX.md                  # Main index (start here)
├── DYNAMIC_TOOL_CONFIG.md         # Tool configuration (NEW)
├── DYNAMIC_TOOL_SUMMARY.md        # Quick reference
├── TOOL_CONFIG_MIGRATION.md       # Migration guide
├── TROUBLESHOOTING.md             # General troubleshooting
├── HOW_TO_ADD_TOOLS.md           # Development guide
├── REPOSITORY_MAINTENANCE.md      # This file
├── guides/                        # Specialized guides
│   ├── TOOL_SYSTEM_GUIDE.md
│   └── MEMORY_TROUBLESHOOTING.md
├── setup/                         # Setup guides
│   └── CHECKPOINTER_SETUP.md
└── archive/                       # Historical docs
    └── (old migration guides)
```

### Adding New Documentation

1. **Create in appropriate directory:**
   - Core docs → `docs/`
   - Guides → `docs/guides/`
   - Setup → `docs/setup/`
   - Archive → `docs/archive/`

2. **Update DOCS_INDEX.md:**
   - Add link to new documentation
   - Update relevant section

3. **Follow naming convention:**
   - Use UPPERCASE for main docs
   - Use descriptive names
   - Keep names short

## 🔄 Regular Maintenance Tasks

### Weekly
- [ ] Run cleanup script: `./scripts/cleanup.sh`
- [ ] Check git status
- [ ] Review open issues/TODOs

### Monthly
- [ ] Update dependencies: `pip list --outdated`
- [ ] Review documentation for accuracy
- [ ] Check for security updates
- [ ] Archive old documentation

### Before Commit
- [ ] Run cleanup script
- [ ] Run tests: `pytest tests/`
- [ ] Check no credentials exposed
- [ ] Review changes: `git diff`

## 🔐 Security Checks

### Never Commit These
```bash
# Credentials
client_secret.json
token.pickle
.env

# API Keys
*_api_key.txt
*_token.txt
*.pem
*.key

# Database credentials
*.db
*.sqlite
```

### Check for Leaked Credentials
```bash
# Check git history
git log -p | grep -i "password\|api_key\|secret"

# Check current files
grep -r "password\|api_key\|secret" . --exclude-dir=.git
```

## 📊 Repository Health

### Good Signs
- ✅ All tests pass
- ✅ No unnecessary files
- ✅ Clean git status
- ✅ Documentation up to date
- ✅ No credentials in code

### Warning Signs
- ⚠️ Large uncommitted changes
- ⚠️ Many cache files
- ⚠️ Outdated dependencies
- ⚠️ Missing documentation
- ⚠️ Failing tests

## 🚀 Quick Commands

```bash
# Clean repository
./scripts/cleanup.sh

# Check status
git status

# Run tests
pytest tests/

# Update dependencies
pip install -r requirements.txt --upgrade

# Check documentation links
grep -r "](.*\.md)" docs/ | grep -v "http"
```

## 📚 Additional Resources

- [Git Best Practices](https://git-scm.com/book/en/v2)
- [Python Project Structure](https://docs.python-guide.org/writing/structure/)
- [Documentation Guide](./DOCS_INDEX.md)

---

**Pro Tip:** Run `./scripts/cleanup.sh` before every commit to keep your repository clean!
