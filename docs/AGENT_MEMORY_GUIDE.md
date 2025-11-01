## Agent & Memory Configuration Guide

## Overview

The WhatsApp HR Assistant now supports **multiple agent types** and **memory backends**, giving you flexibility to choose the best configuration for your needs.

## Quick Start

Edit `.env` to configure:

```bash
# Choose your agent
AGENT_TYPE=simple_react  # or complex_langgraph, hr_agent

# Choose your memory
MEMORY_TYPE=postgres  # or buffer, summary, sqlite, memory, openmemory
```

## Available Agents

### 1. Simple ReAct Agent (`simple_react`)

**Description:** Straightforward ReAct (Reasoning + Acting) agent using LangChain

**Features:**
- ✅ Clear reasoning steps
- ✅ Simple conversation memory
- ✅ Easy to understand and debug
- ✅ Fast execution

**Best For:** Simple tasks, quick responses, debugging, learning

**Compatible Memory:** buffer, summary, openmemory

**Example:**
```python
from src.core.agents.agent_factory import AgentFactory, AgentType, MemoryType

agent = AgentFactory.create_agent(
    agent_type=AgentType.SIMPLE_REACT,
    llm=my_llm,
    tools=my_tools,
    memory_type=MemoryType.BUFFER
)

response = agent.invoke("Find candidates with Python skills")
```

### 2. Complex LangGraph Agent (`complex_langgraph`)

**Description:** Advanced multi-node graph agent with reflection and conditional routing

**Features:**
- ✅ Multi-node workflow graph
- ✅ Conditional routing based on agent decisions
- ✅ Self-reflection and critique capabilities
- ✅ Persistent memory via checkpointer
- ✅ Error handling and recovery
- ✅ Human-in-the-loop support

**Best For:** Complex workflows, multi-step tasks, production use

**Compatible Memory:** postgres, sqlite, memory (LangGraph checkpointers)

**Workflow:**
```
Input → Planner → Executor → Tools → Reflector → Responder → Output
          ↓                      ↓         ↓
       (plans)              (uses tools) (critiques)
```

**Example:**
```python
agent = AgentFactory.create_agent(
    agent_type=AgentType.COMPLEX_LANGGRAPH,
    llm=my_llm,
    tools=my_tools,
    memory_type=MemoryType.POSTGRES,
    memory_config={"connection_string": "postgresql://..."}
)

response = agent.invoke("Process all CVs and schedule top candidates")
```

### 3. HR Agent (`hr_agent`)

**Description:** Existing specialized HR recruitment agent (default, backwards compatible)

**Features:**
- ✅ Recruitment-specific workflows
- ✅ CV processing
- ✅ Interview scheduling
- ✅ Email communication
- ✅ Proven production agent

**Best For:** HR recruitment tasks (current default)

**Compatible Memory:** postgres, sqlite

## Available Memory Types

### 1. Conversation Buffer (`buffer`)

**Description:** Stores full conversation history in memory

**Pros:**
- Simple and fast
- Complete history
- No setup required

**Cons:**
- Limited by context window
- No persistence (lost on restart)
- Can get expensive with long conversations

**Use Case:** Short conversations, testing, development

**Configuration:**
```bash
MEMORY_TYPE=buffer
```

### 2. Conversation Summary (`summary`)

**Description:** Summarizes conversation to save tokens

**Pros:**
- Token efficient
- Handles long conversations
- Maintains key points

**Cons:**
- May lose some details
- Extra LLM calls for summarization

**Use Case:** Long conversations, token optimization

**Configuration:**
```bash
MEMORY_TYPE=summary
```

### 3. PostgreSQL Checkpointer (`postgres`)

**Description:** Persistent storage in PostgreSQL database

**Pros:**
- Fully persistent
- Scalable
- Multi-user support
- Production-ready

**Cons:**
- Requires PostgreSQL database
- More complex setup

**Use Case:** **Production environments** (recommended)

**Configuration:**
```bash
MEMORY_TYPE=postgres
DATABASE_URL=postgresql://user:pass@host:5432/dbname
```

### 4. SQLite Checkpointer (`sqlite`)

**Description:** Local file-based persistent storage

**Pros:**
- Persistent
- No external database needed
- Simple setup

**Cons:**
- Single-user
- File-based limitations

**Use Case:** Development, single-user applications

**Configuration:**
```bash
MEMORY_TYPE=sqlite
# Optional: specify path (defaults to memory)
SQLITE_DB_PATH=./data/agent_memory.db
```

### 5. In-Memory Checkpointer (`memory`)

**Description:** Temporary in-memory storage

**Pros:**
- Very fast
- Simple
- No setup

**Cons:**
- Not persistent
- Lost on restart

**Use Case:** Testing, development, demos

**Configuration:**
```bash
MEMORY_TYPE=memory
```

### 6. OpenMemory (`openmemory`) 🆕

**Description:** Self-hosted AI memory engine with semantic search

**Pros:**
- Semantic memory search
- Multi-sector storage (episodic, semantic, procedural, emotional, reflective)
- Graph-based memory linking
- Privacy-focused (self-hosted)
- 2-3× faster contextual recall
- Explainable reasoning paths

**Cons:**
- Requires external OpenMemory service
- Additional setup needed

**Use Case:** Advanced memory needs, long-term recall, semantic search

**Setup:**

1. **Install OpenMemory:**
```bash
# Clone OpenMemory repository
git clone https://github.com/CaviraOSS/OpenMemory.git
cd openmemory/backend

# Install dependencies
npm install

# Configure
cp .env.example .env
# Edit .env with your settings

# Run
npm run dev  # or docker-compose up for production
```

2. **Configure in .env:**
```bash
MEMORY_TYPE=openmemory
OPENMEMORY_URL=http://localhost:3000
OPENMEMORY_API_KEY=your_api_key_here  # optional
```

3. **Use:**
```python
agent = AgentFactory.create_agent(
    agent_type=AgentType.SIMPLE_REACT,
    llm=my_llm,
    tools=my_tools,
    memory_type=MemoryType.OPENMEMORY,
    memory_config={
        "user_id": "user_123",
        "max_context_messages": 20,
        "min_similarity": 0.6
    }
)
```

**OpenMemory Features:**
- **Hierarchical Memory Decomposition (HMD)**: Multi-sector cognitive storage
- **Semantic Search**: Find relevant memories by meaning, not just keywords
- **Graph Linking**: Memories connect like biological memory
- **Composite Retrieval**: `0.6 × similarity + 0.2 × salience + 0.1 × recency + 0.1 × link_weight`

## Configuration Matrix

| Agent Type | Recommended Memory | Alternative Memories |
|-----------|-------------------|---------------------|
| simple_react | buffer | summary, openmemory |
| complex_langgraph | postgres | sqlite, memory |
| hr_agent | postgres | sqlite |

## Usage Examples

### Example 1: Simple Setup (Development)

```bash
# .env
AGENT_TYPE=simple_react
MEMORY_TYPE=buffer
```

### Example 2: Production Setup

```bash
# .env
AGENT_TYPE=complex_langgraph
MEMORY_TYPE=postgres
DATABASE_URL=postgresql://user:pass@host:5432/dbname
```

### Example 3: Advanced Memory

```bash
# .env
AGENT_TYPE=simple_react
MEMORY_TYPE=openmemory
OPENMEMORY_URL=http://localhost:3000
```

### Example 4: Programmatic Selection

```python
from src.core.agents.agent_factory import AgentFactory, AgentType, MemoryType

# Create simple agent with OpenMemory
agent = AgentFactory.create_agent(
    agent_type=AgentType.SIMPLE_REACT,
    llm=llm,
    tools=tools,
    memory_type=MemoryType.OPENMEMORY,
    memory_config={
        "user_id": session_id,
        "max_context_messages": 15
    }
)

# Or complex agent with PostgreSQL
agent = AgentFactory.create_agent(
    agent_type=AgentType.COMPLEX_LANGGRAPH,
    llm=llm,
    tools=tools,
    memory_type=MemoryType.POSTGRES,
    memory_config={
        "connection_string": DATABASE_URL
    },
    agent_config={
        "max_iterations": 15,
        "enable_reflection": True
    }
)
```

## Getting Agent/Memory Information

```python
from src.core.agents.agent_factory import AgentFactory, AgentType, MemoryType

# Get agent info
info = AgentFactory.get_agent_info(AgentType.COMPLEX_LANGGRAPH)
print(info["description"])
print(info["features"])

# Get memory info
mem_info = AgentFactory.get_memory_info(MemoryType.OPENMEMORY)
print(mem_info["pros"])
print(mem_info["cons"])

# Get compatible memories for an agent
compatible = AgentFactory.list_compatible_memories(AgentType.SIMPLE_REACT)
print(f"Compatible memories: {compatible}")

# Get recommended memory
recommended = AgentFactory.get_recommended_memory(AgentType.COMPLEX_LANGGRAPH)
print(f"Recommended: {recommended}")
```

## Migration Guide

### From Existing HR Agent

The existing HR agent continues to work as default:

```bash
# .env (no changes needed)
AGENT_TYPE=hr_agent  # or omit, this is default
MEMORY_TYPE=postgres
```

### To Simple ReAct Agent

```bash
# .env
AGENT_TYPE=simple_react
MEMORY_TYPE=buffer  # or summary, openmemory
```

### To Complex LangGraph Agent

```bash
# .env
AGENT_TYPE=complex_langgraph
MEMORY_TYPE=postgres  # recommended
```

## Performance Comparison

| Feature | Simple ReAct | Complex LangGraph | HR Agent |
|---------|-------------|-------------------|----------|
| Speed | ⚡⚡⚡ Fast | ⚡⚡ Medium | ⚡⚡ Medium |
| Complexity | 🔹 Simple | 🔹🔹🔹 Complex | 🔹🔹 Medium |
| Reflection | ❌ No | ✅ Yes | ❌ No |
| Multi-step | ✅ Basic | ✅ Advanced | ✅ Basic |
| Production Ready | ⚠️ Testing | ✅ Yes | ✅ Yes |

## Troubleshooting

### OpenMemory Connection Issues

```python
# Test OpenMemory connection
from src.core.memory.openmemory_client import create_openmemory_client
import asyncio

async def test():
    client = create_openmemory_client()
    healthy = await client.health_check()
    print(f"OpenMemory healthy: {healthy}")

asyncio.run(test())
```

### Memory Not Persisting

- Check `DATABASE_URL` is set correctly for postgres/sqlite
- Verify database is accessible
- Check file permissions for SQLite

### Agent Not Using Tools

- Verify tools are loaded: `len(agent.tools) > 0`
- Check tool descriptions are clear
- Try increasing `max_iterations`

## Best Practices

1. **Development:** Use `simple_react` + `buffer` for quick testing
2. **Production:** Use `complex_langgraph` + `postgres` for reliability
3. **Long-term Memory:** Use `openmemory` for semantic recall
4. **Token Optimization:** Use `summary` memory for long conversations
5. **Multi-user:** Always use `postgres` checkpointer

## References

- [LangChain Documentation](https://python.langchain.com/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [OpenMemory GitHub](https://github.com/CaviraOSS/OpenMemory)
- [ReAct Paper](https://arxiv.org/abs/2210.03629)
