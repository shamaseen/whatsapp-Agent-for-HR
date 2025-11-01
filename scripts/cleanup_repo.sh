#!/bin/bash
# Repository cleanup script
# Removes obsolete files and directories

echo "========================================="
echo "Repository Cleanup Script"
echo "========================================="
echo ""

# Track what we're removing
REMOVED=()

# Remove old structure
if [ -d "out/old_structure_v2" ]; then
    SIZE=$(du -sh out/old_structure_v2 | cut -f1)
    echo "Removing old structure: out/old_structure_v2 ($SIZE)"
    rm -rf out/old_structure_v2
    REMOVED+=("out/old_structure_v2/")
fi

# Remove ULTIMATE test files (we have better, more focused tests)
if [ -f "ULTIMATE_EXHAUSTIVE_TEST_SUITE.py" ]; then
    SIZE=$(ls -lh ULTIMATE_EXHAUSTIVE_TEST_SUITE.py | awk '{print $5}')
    echo "Removing: ULTIMATE_EXHAUSTIVE_TEST_SUITE.py ($SIZE)"
    rm ULTIMATE_EXHAUSTIVE_TEST_SUITE.py
    REMOVED+=("ULTIMATE_EXHAUSTIVE_TEST_SUITE.py")
fi

if [ -f "ULTIMATE_MASTER_COMPREHENSIVE_TEST.py" ]; then
    SIZE=$(ls -lh ULTIMATE_MASTER_COMPREHENSIVE_TEST.py | awk '{print $5}')
    echo "Removing: ULTIMATE_MASTER_COMPREHENSIVE_TEST.py ($SIZE)"
    rm ULTIMATE_MASTER_COMPREHENSIVE_TEST.py
    REMOVED+=("ULTIMATE_MASTER_COMPREHENSIVE_TEST.py")
fi

# Remove temporary credential files
if [ -f ".webex_token.json" ]; then
    SIZE=$(ls -lh .webex_token.json | awk '{print $5}')
    echo "Removing: .webex_token.json ($SIZE)"
    rm .webex_token.json
    REMOVED+=(".webex_token.json")
fi

# Check if out/ is now empty
if [ -d "out" ] && [ -z "$(ls -A out)" ]; then
    echo "Removing empty directory: out/"
    rmdir out
    REMOVED+=("out/")
fi

echo ""
echo "========================================="
echo "Cleanup Summary"
echo "========================================="
echo "Items removed: ${#REMOVED[@]}"
for item in "${REMOVED[@]}"; do
    echo "  - $item"
done
echo ""
echo "Cleanup complete!"
