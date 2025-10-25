# LangGraph Checkpointer Setup

## ✅ Using PostgreSQL Checkpointer

The application now uses LangGraph's `PostgresSaver` for automatic conversation memory management.

---

## How It Works

### Database Tables Created:
The checkpointer automatically creates these tables in your existing database:

1. **`checkpoints`** - Stores conversation states
   - Columns: thread_id, checkpoint_ns, checkpoint_id, parent_checkpoint_id, type, checkpoint, metadata

2. **`checkpoint_writes`** - Stores intermediate writes
   - Columns: thread_id, checkpoint_ns, checkpoint_id, task_id, idx, channel, type, value

3. **`checkpoint_blobs`** (if needed) - Stores large data
   - Columns: thread_id, checkpoint_ns, channel, type, blob

### Memory Flow:

```
User sends message (thread_id = phone number)
    ↓
Agent loads previous checkpoint for this thread_id
    ↓
Agent processes message with history
    ↓
Agent saves new checkpoint automatically
    ↓
Next message from same user has full history!
```

---

## Configuration

### In `.env`:
```bash
# Same database used for everything
DATABASE_URL=postgresql://user:password@localhost/dbname
```

### Tables in Database:
- `checkpoints` - LangGraph conversation memory
- `checkpoint_writes` - LangGraph intermediate states
- `conversation_history` - Old memory (not used)
- `request_logs` - Request logging
- `tool_executions` - Tool execution logs

---

## Key Features

### 1. Automatic Setup
```python
# On first run, creates tables automatically
checkpointer.setup()  # Creates checkpoints, checkpoint_writes tables
```

### 2. Thread-Based Memory
```python
# Each user gets their own thread
config = {"configurable": {"thread_id": sender_phone}}
result = agent.invoke(input, config=config)

# LangGraph automatically:
# - Loads previous messages for this thread_id
# - Saves new messages after execution
```

### 3. Connection Management
```python
# Single persistent connection with:
# - autocommit=True (for concurrent index creation)
# - prepare_threshold=None (avoids prepared statement cache issues)
```

---

## Verification

### Check Tables Exist:
```sql
-- Connect to database
psql $DATABASE_URL

-- List tables
\dt

-- Should see:
-- checkpoints
-- checkpoint_writes
-- conversation_history (old, not used)
-- request_logs
-- tool_executions
```

### Check Data:
```sql
-- View checkpoints
SELECT thread_id, checkpoint_id, created_at
FROM checkpoints
ORDER BY created_at DESC
LIMIT 10;

-- Count conversations per user
SELECT thread_id, COUNT(*)
FROM checkpoints
GROUP BY thread_id;
```

---

## Connection Settings

### Important Parameters:
```python
psycopg.connect(
    db_url,
    autocommit=True,          # Required for CREATE INDEX CONCURRENTLY
    prepare_threshold=None,   # Avoid "prepared statement does not exist" error
)
```

### Why `prepare_threshold=None`?
- PostgreSQL prepared statements can cause errors in concurrent environments
- Setting to `None` disables prepared statement caching
- Each query executes directly without caching

---

## Startup Output

### Successful Setup:
```
✅ LangGraph PostgreSQL checkpointer tables initialized
✅ Loaded MCP tools: 8 tools registered
✅ Agent configured with 1 tools
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Tables Already Exist:
```
✅ Checkpointer tables already exist
✅ Loaded MCP tools: 8 tools registered
✅ Agent configured with 1 tools
INFO:     Uvicorn running on http://0.0.0.0:8000
```

---

## Testing Memory

### Send Test Messages:
```bash
# Message 1
curl -X POST http://localhost:8000/webhook/whatsapp \
  -H "Content-Type: application/json" \
  -d '{
    "message_type": "incoming",
    "conversation": {
      "labels": ["hr"],
      "meta": {"sender": {"phone_number": "+962776241974"}}
    },
    "content": "Hello, my name is John"
  }'

# Message 2 (should remember name)
curl -X POST http://localhost:8000/webhook/whatsapp \
  -H "Content-Type: application/json" \
  -d '{
    "message_type": "incoming",
    "conversation": {
      "labels": ["hr"],
      "meta": {"sender": {"phone_number": "+962776241974"}}
    },
    "content": "What is my name?"
  }'
```

### Verify in Database:
```sql
-- Check conversation for this user
SELECT * FROM checkpoints
WHERE thread_id = '962776241974'
ORDER BY created_at;
```

---

## Troubleshooting

### Error: "prepared statement does not exist"
**Solution:** Already fixed with `prepare_threshold=None`

### Error: "cannot CREATE INDEX CONCURRENTLY inside a transaction"
**Solution:** Already fixed with `autocommit=True`

### Error: "relation checkpoints does not exist"
**Check:**
1. DATABASE_URL is correct
2. Database user has CREATE TABLE permissions
3. Application started successfully (check logs)

**Verify:**
```bash
psql $DATABASE_URL -c "\dt"
```

### Memory Not Persisting
**Check:**
1. Same phone number used in both messages
2. Checkpoints table has data: `SELECT COUNT(*) FROM checkpoints;`
3. No errors in application logs

---

## Migration from Old Memory

### Old ConversationMemory (Not Used):
```python
memory = ConversationMemory(session_id)
memory.add_message("user", "Hello")
history = memory.get_history()
```

### New LangGraph Checkpointer (Current):
```python
config = {"configurable": {"thread_id": session_id}}
result = agent.invoke(input, config=config)
# Memory automatically managed!
```

### Data Migration:
The old `conversation_history` table is not used anymore. If you want to migrate:

```sql
-- Old data in conversation_history
-- New data in checkpoints/checkpoint_writes

-- No migration needed - just start fresh
-- Previous conversations will be in checkpoints going forward
```

---

## Summary

✅ **Setup:** Automatic table creation
✅ **Storage:** Same DATABASE_URL as everything else
✅ **Thread ID:** Uses phone number
✅ **Memory:** Automatic load/save
✅ **Tables:** checkpoints, checkpoint_writes
✅ **Connection:** Persistent with autocommit=True
✅ **Errors:** Fixed with prepare_threshold=None

**Conversation memory now fully managed by LangGraph!** 🎉
