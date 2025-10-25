#!/usr/bin/env python3
"""
Diagnostic script to test memory persistence with detailed logging.
"""
import psycopg
from langchain_core.messages import HumanMessage, AIMessage
from agents.hr_agent import create_agent
from config import settings

print("="*80)
print("MEMORY DIAGNOSTIC TEST")
print("="*80 + "\n")

# Clear previous test data
test_thread = "diagnostic_test_12345"
print(f"Test thread ID: {test_thread}")

conn = psycopg.connect(settings.DATABASE_URL)
with conn.cursor() as cur:
    cur.execute("DELETE FROM checkpoints WHERE thread_id = %s", (test_thread,))
    cur.execute("DELETE FROM checkpoint_writes WHERE thread_id = %s", (test_thread,))
conn.commit()
print("✅ Cleared previous test data\n")

# Create agent
print("Creating agent...")
agent = create_agent()
print(f"✅ Agent type: {type(agent).__name__}")
print(f"✅ Has checkpointer: {agent.checkpointer is not None}")
if agent.checkpointer:
    print(f"✅ Checkpointer type: {type(agent.checkpointer).__name__}\n")

# Message 1
print("="*80)
print("MESSAGE 1: 'My name is Ahmad'")
print("="*80)

result1 = agent.invoke(
    {"messages": [HumanMessage(content="My name is Ahmad")]},
    config={"configurable": {"thread_id": test_thread}}
)

print(f"\n📊 Result 1 Statistics:")
print(f"   Messages in result: {len(result1['messages'])}")
print(f"   Message types: {[type(m).__name__ for m in result1['messages']]}")

# Check database
with conn.cursor() as cur:
    cur.execute("SELECT COUNT(*) FROM checkpoints WHERE thread_id = %s", (test_thread,))
    count1 = cur.fetchone()[0]
    print(f"   Checkpoints in DB: {count1}")

# Get AI response
for msg in reversed(result1['messages']):
    if isinstance(msg, AIMessage) and msg.content:
        print(f"\n🤖 AI Response 1: {msg.content[:150]}...")
        break

# Message 2
print("\n" + "="*80)
print("MESSAGE 2: 'What is my name?'")
print("="*80)

result2 = agent.invoke(
    {"messages": [HumanMessage(content="What is my name?")]},
    config={"configurable": {"thread_id": test_thread}}
)

print(f"\n📊 Result 2 Statistics:")
print(f"   Messages in result: {len(result2['messages'])}")
print(f"   Message types: {[type(m).__name__ for m in result2['messages']]}")

# Check database
with conn.cursor() as cur:
    cur.execute("SELECT COUNT(*) FROM checkpoints WHERE thread_id = %s", (test_thread,))
    count2 = cur.fetchone()[0]
    print(f"   Checkpoints in DB: {count2}")

# Get AI response
final_response = None
for msg in reversed(result2['messages']):
    if isinstance(msg, AIMessage) and msg.content:
        final_response = msg.content
        print(f"\n🤖 AI Response 2: {msg.content}")
        break

conn.close()

# Verify
print("\n" + "="*80)
print("VERIFICATION")
print("="*80)

print(f"\n1. Message count should increase:")
print(f"   Result 1: {len(result1['messages'])} messages")
print(f"   Result 2: {len(result2['messages'])} messages")
if len(result2['messages']) > len(result1['messages']):
    print("   ✅ Message count increased")
else:
    print("   ❌ Message count did NOT increase - history not loaded!")

print(f"\n2. Checkpoint count should increase:")
print(f"   After message 1: {count1} checkpoints")
print(f"   After message 2: {count2} checkpoints")
if count2 > count1:
    print("   ✅ Checkpoints being saved")
else:
    print("   ❌ Checkpoints NOT being saved!")

print(f"\n3. Agent should remember the name:")
if final_response and "ahmad" in final_response.lower():
    print(f"   ✅ Agent remembered: '{final_response}'")
else:
    print(f"   ❌ Agent did NOT remember!")
    print(f"   Response: '{final_response}'")

print("\n" + "="*80)

# Final diagnosis
if (len(result2['messages']) > len(result1['messages']) and
    count2 > count1 and
    final_response and "ahmad" in final_response.lower()):
    print("✅ ✅ ✅ MEMORY IS WORKING CORRECTLY!")
else:
    print("❌ MEMORY IS NOT WORKING - See issues above")
    print("\nPossible causes:")
    print("  1. Checkpointer not attached to agent")
    print("  2. Thread ID not being used correctly")
    print("  3. Messages not being loaded from checkpoints")
    print("  4. Database connection issue")

print("="*80)
