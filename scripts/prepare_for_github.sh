#!/bin/bash
# Prepare repository for GitHub push
# Removes test files, results, and temporary files

echo "================================================================================"
echo "PREPARING REPOSITORY FOR GITHUB"
echo "================================================================================"

# Track what we're removing
REMOVED=()
TOTAL_SIZE=0

# Function to get file size in KB
get_size() {
    local file=$1
    if [ -f "$file" ]; then
        ls -lh "$file" | awk '{print $5}'
    fi
}

# Remove test files
echo ""
echo "Removing test files..."
for file in test_*.py test_*.json comprehensive_test_*.py comprehensive_test_*.json \
           agent_test_*.json config_combination_*.json final_validation_*.json \
           notebook_execution_*.json NOTEBOOK_TEST_REPORT.md TESTING_SUMMARY.md \
           DEEP_TESTING_REPORT.md MCP_*.md; do
    if [ -f "$file" ]; then
        size=$(get_size "$file")
        echo "  Removing: $file ($size)"
        rm "$file"
        REMOVED+=("$file")
    fi
done

# Remove test notebooks execution results
echo ""
echo "Removing notebook execution results..."
for file in tests/notebooks/*_executed.ipynb tests/notebooks/*.html; do
    if [ -f "$file" ]; then
        size=$(get_size "$file")
        echo "  Removing: $file ($size)"
        rm "$file"
        REMOVED+=("$file")
    fi
done

# Remove temporary credential files
echo ""
echo "Removing temporary credential files..."
for file in .webex_token.json token.pickle client_secret.json; do
    if [ -f "$file" ]; then
        size=$(get_size "$file")
        echo "  Removing: $file ($size)"
        rm "$file"
        REMOVED+=("$file")
    fi
done

# Remove log files
echo ""
echo "Removing log files..."
for file in *.log; do
    if [ -f "$file" ]; then
        size=$(get_size "$file")
        echo "  Removing: $file ($size)"
        rm "$file"
        REMOVED+=("$file")
    fi
done

# Remove __pycache__ directories
echo ""
echo "Removing Python cache directories..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null && echo "  Removed __pycache__ directories"
find . -type d -name "*.pyc" -delete 2>/dev/null && echo "  Removed .pyc files"

# Remove .pytest_cache
echo ""
echo "Removing pytest cache..."
rm -rf .pytest_cache 2>/dev/null && echo "  Removed .pytest_cache"

# Check for other test artifacts
echo ""
echo "Removing other test artifacts..."
for pattern in ".coverage" "htmlcov" "*.pytest_cache"; do
    if ls $pattern 2>/dev/null | grep -q .; then
        ls -lh $pattern 2>/dev/null | head -5
        rm -rf $pattern 2>/dev/null
        REMOVED+=("$pattern")
    fi
done

# Create clean .gitignore if not exists or update
echo ""
echo "Checking .gitignore..."
if [ ! -f ".gitignore" ]; then
    cat > .gitignore << 'EOF'
# Byte-compiled / optimized / DLL files
__pycache__/
*.py[cod]
*$py.class
*.so

# Distribution / packaging
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

# PyInstaller
*.manifest
*.spec

# Installer logs
pip-log.txt
pip-delete-this-directory.txt

# Unit test / coverage reports
htmlcov/
.tox/
.coverage
.coverage.*
.cache
.pytest_cache/
nosetests.xml
coverage.xml
*.cover
.hypothesis/
.pytest_cache/

# Environment variables
.env
.env.local
.env.*.local

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Logs
*.log
logs/

# Test results
test_*.json
test_*.py
comprehensive_test_*.json
comprehensive_test_*.py
agent_test_*.json
config_combination_*.json
final_validation_*.json
notebook_execution_*.json

# Temporary files
*.tmp
*.temp
token.pickle
client_secret.json
.webex_token.json

# MCP Tool reports
NOTEBOOK_TEST_REPORT.md
TESTING_SUMMARY.md
DEEP_TESTING_REPORT.md
MCP_*.md

# Notebook outputs
tests/notebooks/*_executed.ipynb
tests/notebooks/*.html
EOF
    echo "  Created .gitignore"
else
    echo "  .gitignore already exists"
fi

# Print summary
echo ""
echo "================================================================================"
echo "CLEANUP SUMMARY"
echo "================================================================================"
echo "Items removed: ${#REMOVED[@]}"
for item in "${REMOVED[@]}"; do
    echo "  - $item"
done

echo ""
echo "Repository is now clean and ready for GitHub!"
echo ""
echo "Next steps:"
echo "  1. Review the files (git status)"
echo "  2. Add files to git (git add .)"
echo "  3. Commit (git commit -m 'Clean repository for production')"
echo "  4. Push to GitHub (git push)"
echo ""
echo "================================================================================"
