#!/usr/bin/env python3
"""
Simple import test for WhatsApp HR Assistant
Tests basic structure and dependencies
"""

import sys
import os

# Add project root to path
project_root = os.path.abspath('../..')
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def test_dependencies():
    """Test if required dependencies are available"""
    print("🔍 Testing Dependencies:")
    
    dependencies = [
        ("pydantic", "pydantic"),
        ("pydantic_settings", "pydantic_settings"),
        ("fastapi", "fastapi"),
        ("langchain", "langchain"),
        ("langgraph", "langgraph"),
        ("langchain_google_genai", "langchain_google_genai"),
        ("psycopg", "psycopg"),
        ("google", "google"),
        ("sqlalchemy", "sqlalchemy")
    ]
    
    missing_deps = []
    for dep_name, module_name in dependencies:
        try:
            __import__(module_name)
            print(f"✅ {dep_name}")
        except ImportError:
            print(f"❌ {dep_name} - MISSING")
            missing_deps.append(dep_name)
    
    return missing_deps

def test_file_structure():
    """Test if project files exist"""
    print("\n📁 Testing File Structure:")
    
    files_to_check = [
        "main.py",
        "config.py", 
        "requirements.txt",
        "agents/hr_agent.py",
        "agents/tool_factory.py",
        "agents/prompts.py",
        "services/memory_langgraph.py",
        "services/request_logger.py",
        "services/google_drive.py",
        "services/whatsapp.py",
        "models/schemas.py",
        "models/request_logs.py",
        "mcp_integration/tools/base.py",
        "mcp_integration/tools/google/gmail_mcp.py",
        "mcp_integration/tools/utilities/datetime_mcp.py"
    ]
    
    missing_files = []
    for file_path in files_to_check:
        # Check relative to current directory (project root)
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING")
            missing_files.append(file_path)
    
    return missing_files

def test_imports():
    """Test critical imports (with graceful failure)"""
    print("\n📦 Testing Critical Imports:")
    
    imports_to_test = [
        ("Config", "config"),
        ("MCP Base", "mcp_integration.tools.base"),
        ("Agent", "agents.hr_agent"),
        ("Tool Factory", "agents.tool_factory"),
        ("Memory", "services.memory_langgraph"),
        ("Request Logger", "services.request_logger"),
        ("WhatsApp", "services.whatsapp"),
        ("Models", "models.schemas"),
        ("Main App", "main")
    ]
    
    failed_imports = []
    for name, module_path in imports_to_test:
        try:
            # Add current directory to path for imports
            import sys
            if '.' not in sys.path:
                sys.path.insert(0, '.')
            __import__(module_path)
            print(f"✅ {name}")
        except Exception as e:
            print(f"❌ {name}: {e}")
            failed_imports.append(name)
    
    return failed_imports

def main():
    """Run all tests"""
    print("🧪 WhatsApp HR Assistant - Basic Import Test")
    print("=" * 60)
    
    # Test dependencies
    missing_deps = test_dependencies()
    
    # Test file structure
    missing_files = test_file_structure()
    
    # Test imports
    failed_imports = test_imports()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 TEST SUMMARY")
    print("=" * 60)
    
    if missing_deps:
        print(f"❌ Missing dependencies: {', '.join(missing_deps)}")
        print("   Run: pip install -r requirements.txt")
    else:
        print("✅ All dependencies available")
    
    if missing_files:
        print(f"❌ Missing files: {len(missing_files)}")
    else:
        print("✅ All required files present")
    
    if failed_imports:
        print(f"❌ Failed imports: {', '.join(failed_imports)}")
    else:
        print("✅ All imports successful")
    
    if not missing_deps and not missing_files and not failed_imports:
        print("\n🎉 ALL TESTS PASSED!")
        print("The WhatsApp HR Assistant is ready for use.")
    else:
        print("\n⚠️ Some tests failed. Please check the issues above.")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
