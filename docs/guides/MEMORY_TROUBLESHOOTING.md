# Memory Troubleshooting Guide

## Issue: Agent Says "I do not retain memory of past conversations"

This means the checkpointer is not loading previous messages properly.

---

## Diagnostic Steps

### 1. Check Application Logs

Restart the application and look for:

```bash
python3 main.py
```

**Expected on startup:**
```
✅ LangGraph PostgreSQL checkpointer tables initialized
✅ Loaded MCP tools: 8 tools registered
```

### 2. Send a Test Message

When you send a message, check the logs for:

```
🤖 Processing message from 962778435754... [Request ID: req_xxx]
   Thread ID: 962778435754
   Message count in result: X
   Checkpoints in DB for 962778435754: Y
```

**What to check:**
- `Thread ID` - Should be consistent for same user
- `Message count` - Should increase with each message (2, 4, 6, etc.)
- `Checkpoints in DB` - Should increase (1, 2, 3, etc.)

### 3. Check Database Directly

```bash
python3 check_memory.py
```

**Expected output:**
```
Tables:
  ✅ checkpoints
  ✅ checkpoint_writes

Total checkpoints: 5

Conversations (1 users):
  Thread ID: 962778435754
  Checkpoints: 3
```

### 4. Check Specific User

```bash
python3 check_memory.py 962778435754
```

**Expected:**
```
Found 3 checkpoints:

1. Checkpoint: ...
   Type: checkpoint
   Parent: ...
```

---

## Common Issues & Solutions

### Issue 1: "No checkpoints found in database"

**Possible causes:**
1. Tables not created
2. Connection error
3. Checkpointer not initialized

**Solution:**
```bash
# Check tables exist
psql $DATABASE_URL -c "\dt"

# Should show:
# checkpoints
# checkpoint_writes

# If not, restart application to create them
python3 main.py
```

### Issue 2: "Thread ID changes each time"

**Possible causes:**
1. Phone number format inconsistent
2. Using different identifier

**Solution:**
Check logs for thread_id pattern:
```
   Thread ID: 962778435754    # ✅ Correct (no + or spaces)
   Thread ID: +962 77 843 5754 # ❌ Wrong
```

### Issue 3: "Checkpoints saved but not loaded"

**Possible causes:**
1. Different thread_id between save/load
2. Database connection pooling issue
3. Autocommit not enabled

**Solution:**
```python
# In services/memory_langgraph.py
# Verify connection has:
autocommit=True,
prepare_threshold=None,
```

### Issue 4: "Message count doesn't increase"

**Possible causes:**
1. Checkpointer not saving
2. Loading from wrong thread_id
3. Config not passed correctly

**Solution:**
Check config is passed:
```python
config = {"configurable": {"thread_id": sender_phone}}
result = agent_app.invoke(input, config=config)  # ← Must pass config!
```

---

## Manual Database Check

### Check Tables Exist:
```sql
\c your_database
\dt

-- Should show:
-- checkpoints
-- checkpoint_writes
```

### Check Checkpoints:
```sql
SELECT thread_id, COUNT(*)
FROM checkpoints
GROUP BY thread_id;
```

### Check Specific User:
```sql
SELECT checkpoint_id, type, checkpoint
FROM checkpoints
WHERE thread_id = '962778435754'
ORDER BY checkpoint_id;
```

### View Checkpoint Data:
```sql
SELECT
    thread_id,
    checkpoint_id,
    jsonb_pretty(checkpoint::jsonb) as checkpoint_data
FROM checkpoints
WHERE thread_id = '962778435754'
ORDER BY checkpoint_id DESC
LIMIT 1;
```

---

## Debug Mode

Add extra logging to main.py:

```python
# After invoking agent
print(f"   Thread ID used: {thread_id}")
print(f"   Messages in result: {len(result['messages'])}")
print(f"   Message types: {[type(m).__name__ for m in result['messages']]}")

# Check database
import psycopg
conn = psycopg.connect(settings.DATABASE_URL)
with conn.cursor() as cur:
    cur.execute("SELECT COUNT(*) FROM checkpoints WHERE thread_id = %s", (thread_id,))
    count = cur.fetchone()[0]
    print(f"   DB checkpoints: {count}")
conn.close()
```

---

## Expected Behavior

### First Message:
```
Thread ID: 962778435754
Message count in result: 2 (SystemMessage + HumanMessage)
Checkpoints in DB: 1
```

### Second Message:
```
Thread ID: 962778435754
Message count in result: 4 (SystemMessage + HumanMessage + AIMessage + HumanMessage)
Checkpoints in DB: 2
```

### Third Message:
```
Thread ID: 962778435754
Message count in result: 6 (full history + new message)
Checkpoints in DB: 3
```

---

## Verification Checklist

- [ ] Tables `checkpoints` and `checkpoint_writes` exist
- [ ] Application shows "checkpointer tables initialized"
- [ ] Logs show consistent thread_id for same user
- [ ] `check_memory.py` shows checkpoints being created
- [ ] Message count increases with each message
- [ ] Database query shows checkpoints for thread_id

---

## Fix: Reset and Test

If nothing works, reset and test:

### 1. Clear Old Data
```sql
DELETE FROM checkpoints;
DELETE FROM checkpoint_writes;
```

### 2. Restart Application
```bash
python3 main.py
```

### 3. Send Test Sequence

**Message 1:**
```json
{
  "content": "Hi, my name is Ahmad"
}
```

**Check:**
```bash
python3 check_memory.py 962778435754
# Should show: Found 1 checkpoint
```

**Message 2:**
```json
{
  "content": "What is my name?"
}
```

**Check:**
```bash
python3 check_memory.py 962778435754
# Should show: Found 2 checkpoints
```

**Expected Response:**
```
"Your name is Ahmad."  # ✅ Memory working!
```

---

## Still Not Working?

### Check Connection:
```python
from services.memory_langgraph import get_checkpointer

cp = get_checkpointer()
print(f"Checkpointer: {cp}")
print(f"Connection: {cp.conn}")
print(f"Closed: {cp.conn.closed}")
```

### Check Config Format:
```python
# Must be exactly this format:
config = {
    "configurable": {
        "thread_id": "962778435754"  # String, not int!
    }
}
```

### Check Agent Compilation:
```python
from agents.hr_agent import create_agent

agent = create_agent()
print(f"Has checkpointer: {agent.checkpointer is not None}")
```

---

## Quick Test Script

```python
#!/usr/bin/env python3
from langchain_core.messages import HumanMessage, AIMessage
from agents.hr_agent import create_agent

agent = create_agent()
thread_id = "test_user"

# Message 1
result1 = agent.invoke(
    {"messages": [HumanMessage(content="My name is Ahmad")]},
    config={"configurable": {"thread_id": thread_id}}
)
print(f"Message 1 - Count: {len(result1['messages'])}")

# Message 2
result2 = agent.invoke(
    {"messages": [HumanMessage(content="What is my name?")]},
    config={"configurable": {"thread_id": thread_id}}
)
print(f"Message 2 - Count: {len(result2['messages'])}")

# Check response
for msg in reversed(result2['messages']):
    if isinstance(msg, AIMessage) and msg.content:
        print(f"Response: {msg.content}")
        if "ahmad" in msg.content.lower():
            print("✅ MEMORY WORKING!")
        else:
            print("❌ MEMORY NOT WORKING")
        break
```

---

## Contact Support

If issue persists, provide:
1. Application logs (startup + 2 messages)
2. Output of `python3 check_memory.py`
3. Output of `psql $DATABASE_URL -c "SELECT COUNT(*) FROM checkpoints;"`
4. Thread ID being used

**Remember: Thread ID must be consistent across all messages from the same user!**
