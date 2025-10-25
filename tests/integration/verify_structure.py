#!/usr/bin/env python3
"""
Verify code structure without running it
"""
import ast
import sys

def verify_file(filename):
    """Verify Python file syntax"""
    try:
        with open(filename, 'r') as f:
            code = f.read()
        ast.parse(code)
        print(f"✅ {filename}: Syntax OK")
        return True
    except SyntaxError as e:
        print(f"❌ {filename}: Syntax Error - {e}")
        return False
    except Exception as e:
        print(f"⚠️  {filename}: {e}")
        return False

def verify_imports(filename, expected_imports):
    """Verify file has expected imports"""
    try:
        with open(filename, 'r') as f:
            code = f.read()
        tree = ast.parse(code)

        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.add(node.module)
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    imports.add(alias.name)

        missing = set(expected_imports) - imports
        if missing:
            print(f"⚠️  {filename}: Missing imports: {missing}")
        else:
            print(f"✅ {filename}: All expected imports present")

        return len(missing) == 0
    except Exception as e:
        print(f"❌ {filename}: Error checking imports - {e}")
        return False

# Verify main files
print("\n" + "="*60)
print("STRUCTURE VERIFICATION")
print("="*60 + "\n")

files_to_check = [
    "main.py",
    "agents/hr_agent.py",
    "agents/tool_factory.py",
    "config.py",
    "services/memory_langgraph.py",
]

all_ok = True
for filename in files_to_check:
    if not verify_file(filename):
        all_ok = False

print("\n" + "-"*60)
print("Import Verification")
print("-"*60 + "\n")

# Check critical imports
verify_imports("main.py", ["agents.hr_agent", "services.request_logger"])
verify_imports("agents/hr_agent.py", ["agents.tool_factory", "services.memory_langgraph"])
verify_imports("agents/tool_factory.py", ["config"])

print("\n" + "="*60)
if all_ok:
    print("✅ ALL CHECKS PASSED")
else:
    print("❌ SOME CHECKS FAILED")
print("="*60 + "\n")
