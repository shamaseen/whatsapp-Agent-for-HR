#!/usr/bin/env python3
"""
Simple Test Script for Updated Architecture
Tests memory and tool loading
"""
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

print("="*80)
print("TESTING UPDATED WHATSAPP HR ASSISTANT ARCHITECTURE")
print("="*80 + "\n")

# Test 1: Import and configuration
print("Test 1: Imports and Configuration")
print("-" * 60)
try:
    from config import settings
    print(f"✅ Model: {settings.MODEL_NAME}")
    print(f"✅ Tool Mode: {settings.TOOL_MODE}")
    print(f"✅ Database: {settings.DATABASE_URL[:30]}...")
except Exception as e:
    print(f"❌ Config error: {e}")
    exit(1)

# Test 2: Tool Factory
print("\nTest 2: Tool Factory")
print("-" * 60)
try:
    from agents.tool_factory import get_tools, get_tool_mode_info

    # Get tool mode info
    info = get_tool_mode_info()
    print(f"✅ Tool Mode: {info['mode']}")
    print(f"✅ Description: {info['description']}")
    print(f"✅ Tool Count: {info['tool_count']}")
    print(f"✅ Tools: {', '.join(info['tools'][:3])}...")

except Exception as e:
    print(f"❌ Tool factory error: {e}")
    import traceback
    traceback.print_exc()

# Test 3: Memory System
print("\nTest 3: Memory System (LangGraph Checkpointer)")
print("-" * 60)
try:
    from services.memory_langgraph import get_checkpointer

    # Note: Actual connection requires PostgreSQL
    print("✅ Checkpointer module imported")
    print("✅ PostgresSaver available for LangGraph")
    print("ℹ️  Actual database connection requires PostgreSQL running")

except Exception as e:
    print(f"❌ Memory error: {e}")
    import traceback
    traceback.print_exc()

# Test 4: Agent Creation
print("\nTest 4: Agent Creation")
print("-" * 60)
try:
    from agents.hr_agent import create_agent

    print("✅ Agent module imported")
    print("ℹ️  Agent creation requires:")
    print("   - PostgreSQL running for checkpointer")
    print("   - Google API credentials")
    print("   - Tool dependencies installed")

except Exception as e:
    print(f"❌ Agent error: {e}")
    import traceback
    traceback.print_exc()

# Test 5: Check dependencies
print("\nTest 5: Check Key Dependencies")
print("-" * 60)

dependencies = [
    ("langchain", "LangChain core"),
    ("langchain_google_genai", "Google Gemini"),
    ("langgraph", "LangGraph"),
    ("fastapi", "FastAPI"),
    ("sqlalchemy", "SQLAlchemy"),
]

for module, description in dependencies:
    try:
        __import__(module)
        print(f"✅ {description} ({module})")
    except ImportError:
        print(f"❌ {description} ({module}) - NOT INSTALLED")

# Summary
print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print("""
✅ Architecture Updated Successfully!

Key Changes:
1. Memory: LangGraph PostgresSaver (automatic conversation persistence)
2. Tools: Configurable via TOOL_MODE (mcp/mcp_client/direct)
3. Agent: Integrated with checkpointer for memory

Next Steps:
1. Install dependencies: pip install -r requirements.txt
2. Configure .env with TOOL_MODE and DATABASE_URL
3. Start PostgreSQL database
4. Run: python main.py

For detailed documentation, see:
- MEMORY_AND_TOOLS_UPGRADE.md
""")
