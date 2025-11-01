#!/bin/bash
# Repository Cleanup Script
# Removes temporary files, cache, and build artifacts

set -e  # Exit on error

echo "🧹 Starting repository cleanup..."
echo ""

# Function to safely remove files
safe_remove() {
    if [ -n "$1" ]; then
        echo "  Removing: $1"
        rm -rf "$1" 2>/dev/null || true
    fi
}

# 1. Python cache and bytecode
echo "1. Cleaning Python cache files..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name "*.pyo" -delete 2>/dev/null || true
find . -type f -name "*.pyd" -delete 2>/dev/null || true
find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
echo "  ✅ Python cache cleaned"

# 2. Backup files
echo ""
echo "2. Cleaning backup files..."
find . -type f -name "*.backup" -delete 2>/dev/null || true
find . -type f -name "*.bak" -delete 2>/dev/null || true
find . -type f -name "*~" -delete 2>/dev/null || true
find . -type f -name "*.swp" -delete 2>/dev/null || true
find . -type f -name "*.swo" -delete 2>/dev/null || true
echo "  ✅ Backup files cleaned"

# 3. OS-specific files
echo ""
echo "3. Cleaning OS-specific files..."
find . -type f -name ".DS_Store" -delete 2>/dev/null || true
find . -type f -name "Thumbs.db" -delete 2>/dev/null || true
find . -type f -name "desktop.ini" -delete 2>/dev/null || true
echo "  ✅ OS files cleaned"

# 4. Temporary files
echo ""
echo "4. Cleaning temporary files..."
safe_remove "./tmp"
safe_remove "./temp"
find . -type f -name "*.tmp" -delete 2>/dev/null || true
echo "  ✅ Temporary files cleaned"

# 5. Log files (excluding important ones)
echo ""
echo "5. Cleaning log files..."
find . -type f -name "*.log" -not -path "./logs/important/*" -delete 2>/dev/null || true
echo "  ✅ Log files cleaned"

# 6. Build artifacts
echo ""
echo "6. Cleaning build artifacts..."
safe_remove "./build"
safe_remove "./dist"
safe_remove "./*.egg-info"
echo "  ✅ Build artifacts cleaned"

# 7. Test cache
echo ""
echo "7. Cleaning test cache..."
safe_remove "./.pytest_cache"
safe_remove "./.coverage"
safe_remove "./htmlcov"
echo "  ✅ Test cache cleaned"

# 8. Node modules (if any)
echo ""
echo "8. Cleaning Node modules (if present)..."
if [ -d "./node_modules" ]; then
    safe_remove "./node_modules"
    echo "  ✅ Node modules cleaned"
else
    echo "  ⏭️  No Node modules found"
fi

# Summary
echo ""
echo "="*60
echo "✨ Repository cleanup complete!"
echo "="*60
echo ""
echo "Cleaned:"
echo "  • Python cache (__pycache__, *.pyc)"
echo "  • Backup files (*.backup, *.bak, *~)"
echo "  • OS files (.DS_Store, Thumbs.db)"
echo "  • Temporary files (tmp/, *.tmp)"
echo "  • Log files (*.log)"
echo "  • Build artifacts (build/, dist/)"
echo "  • Test cache (.pytest_cache)"
echo ""
echo "Repository is now clean! 🎉"
echo ""

# Show current size
echo "Current repository size:"
du -sh . 2>/dev/null || echo "  (size check not available)"
echo ""
