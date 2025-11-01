# Database Setup Guide

Complete guide to setting up PostgreSQL database for the WhatsApp HR Assistant.

---

## Overview

The WhatsApp HR Assistant uses PostgreSQL for:
- **Agent Memory**: LangGraph checkpointer for conversation history
- **Request Logging**: Track all incoming messages and AI responses
- **Tool Execution Logs**: Monitor tool usage and performance
- **Candidate Data**: Store CV information and candidate profiles

---

## Prerequisites

- PostgreSQL 13+ installed
- Database user with create privileges
- 1GB+ disk space

---

## Option 1: Local PostgreSQL

### Install PostgreSQL

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

**macOS:**
```bash
brew install postgresql
brew services start postgresql
```

**Windows:**
Download from [postgresql.org](https://www.postgresql.org/download/windows/)

### Create Database

```bash
# Connect as postgres user
sudo -u postgres psql

# Create database and user
CREATE DATABASE whatsapp_hr_assistant;
CREATE USER hr_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE whatsapp_hr_assistant TO hr_user;
\q
```

### Configure .env

```env
DATABASE_URL=postgresql://hr_user:secure_password@localhost:5432/whatsapp_hr_assistant
```

**Important**: Use direct connection port `5432`, not pooler port `6543`

---

## Option 2: Supabase

### Create Supabase Project

1. Visit [supabase.com](https://supabase.com)
2. Sign up/Login
3. Click "New Project"
4. Choose organization
5. Fill in:
   - **Name**: whatsapp-hr-assistant
   - **Database Password**: Generate strong password
6. Click "Create new project"
7. Wait for setup (2-3 minutes)

### Get Connection String

1. Go to Project Settings → Database
2. Copy "Connection String" → "URI"
3. Replace `[YOUR-PASSWORD]` with your database password
4. Add `?sslmode=require` at end

**Example:**
```env
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.xxx.supabase.co:5432/postgres?sslmode=require
```

---

## Initialize Database

### Run Initialization Script

```python
python3 -c "
from src.memory.postgres import get_checkpointer

print('Initializing database...')
checkpointer = get_checkpointer()
print('✅ Database initialized successfully!')
"
```

This creates the required tables:
- `checkpoints` - LangGraph conversation state
- `checkpoint_blobs` - Message data
- `checkpoint_writes` - State updates
- `request_logs` - Request tracking
- `tool_execution_logs` - Tool usage
- `ai_thinking_logs` - AI reasoning

---

## Test Connection

### Test 1: Basic Connection

```python
import psycopg

# Connect to database
conn = psycopg.connect('postgresql://hr_user:secure_password@localhost:5432/whatsapp_hr_assistant')

# Test query
cur = conn.cursor()
cur.execute('SELECT 1;')
result = cur.fetchone()

print(f"✅ Database connected! Test query: {result}")

cur.close()
conn.close()
```

### Test 2: Check Tables

```python
import psycopg

conn = psycopg.connect('postgresql://hr_user:secure_password@localhost:5432/whatsapp_hr_assistant')

cur = conn.cursor()
cur.execute("""
    SELECT table_name 
    FROM information_schema.tables 
    WHERE table_schema = 'public'
    ORDER BY table_name;
""")

tables = cur.fetchall()
print(f"✅ Found {len(tables)} tables:")
for table in tables:
    print(f"   - {table[0]}")

cur.close()
conn.close()
```

---

## Troubleshooting

### Error: `connection refused`

**Cause**: PostgreSQL not running or wrong host/port.

**Solutions**:

1. **Check PostgreSQL is running**
   ```bash
   # Ubuntu/Debian
   sudo systemctl status postgresql
   
   # macOS
   brew services list | grep postgresql
   
   # Windows
   net start postgresql-x64-13
   ```

2. **Check port**
   - Default PostgreSQL port: `5432`
   - Verify in `postgresql.conf`
   - Test with: `telnet localhost 5432`

### Error: `password authentication failed`

**Cause**: Wrong username/password or authentication method.

**Solutions**:

1. **Verify credentials**
   ```bash
   psql -h localhost -U hr_user -d whatsapp_hr_assistant
   ```

2. **Check pg_hba.conf**
   - Location: `/etc/postgresql/13/main/pg_hba.conf`
   - Ensure this line exists:
   ```
   local   all             all                                     md5
   ```
   - Restart PostgreSQL: `sudo systemctl restart postgresql`

### Error: `database "whatsapp_hr_assistant" does not exist`

**Cause**: Database not created.

**Solution**:
```bash
sudo -u postgres createdb whatsapp_hr_assistant
```

### Error: `checkpointer` table not found

**Cause**: Database not initialized.

**Solution**:
```python
from src.memory.postgres import get_checkpointer
checkpointer = get_checkpointer()
```

---

## Production Checklist

### Security

1. **Use strong passwords**
2. **Enable SSL/TLS**
   ```env
   DATABASE_URL=postgresql://user:pass@host:5432/db?sslmode=require
   ```
3. **Restrict network access**
   - Use firewall rules
   - Whitelist application IPs
4. **Rotate credentials regularly**

### Performance

1. **Connection Pooling**
   - Use connection pooler (PgBouncer)
   - For Supabase, use pooler URL: `5432` for checkpointer, `6543` for app

2. **Indexes**
   ```sql
   CREATE INDEX CONCURRENTLY idx_checkpoints_thread_id 
   ON checkpoints(thread_id);
   
   CREATE INDEX CONCURRENTLY idx_request_logs_timestamp 
   ON request_logs(timestamp);
   ```

3. **Regular Maintenance**
   ```sql
   -- Analyze table statistics
   ANALYZE;
   
   -- Vacuum to reclaim space
   VACUUM;
   ```

### Backup

```bash
# Backup database
pg_dump -h localhost -U hr_user whatsapp_hr_assistant > backup.sql

# Restore database
psql -h localhost -U hr_user whatsapp_hr_assistant < backup.sql
```

---

## Database Schema

### Core Tables

#### checkpoints
Stores LangGraph conversation state:
```sql
- thread_id (TEXT, PK)
- checkpoint_ns (TEXT, PK)
- checkpoint_id (TEXT, PK)
- checkpoint (JSONB)
- metadata (JSONB)
```

#### request_logs
Tracks all requests:
```sql
- id (SERIAL, PK)
- request_id (VARCHAR, UNIQUE)
- timestamp (TIMESTAMP)
- sender_phone (VARCHAR)
- user_message (TEXT)
- ai_response (TEXT)
- processing_time_ms (FLOAT)
- status (VARCHAR)
```

### View Schema

```sql
-- View all tables
\dt

-- View table structure
\d request_logs

-- View indexes
\di
```

---

## Memory Types Comparison

| Memory Type | Storage | Persistence | Use Case |
|-------------|---------|-------------|----------|
| `buffer` | RAM | No restart | Testing, short sessions |
| `postgres` | PostgreSQL | Yes ✅ | **Production** |
| `sqlite` | SQLite file | Yes | Single-user, dev |
| `memory` | RAM + disk | Partial | Quick development |

---

## See Also

- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Supabase Docs](https://supabase.com/docs)
- [LangGraph Checkpointer](https://python.langchain.com/docs/langgraph/checkpointing)

---

**Last Updated**: October 31, 2025
