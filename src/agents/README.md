# Agent System Documentation

> **Complete guide to using the WhatsApp HR Assistant agent system**
> **Last Updated**: October 2025

## 🎯 Overview

The WhatsApp HR Assistant uses a modern agent architecture based on **LangGraph** with two distinct agent types:

1. **Simple ReAct Agent** - Lightweight, easy-to-debug agent for basic tasks
2. **Complex LangGraph Agent** - Production-grade agent with multi-node workflow and reflection

Both agents are powered by **Google Gemini** and equipped with **8+ specialized tools** for HR tasks including Gmail, Calendar, CV processing, and Webex meetings.

---

## 🚀 Quick Start

### Basic Agent Usage

```python
from src.config import settings
from langchain_google_genai import ChatGoogleGenerativeAI
from src.agents.tool_factory import get_tools
from src.agents.complex_agent import create_complex_langgraph_agent

# 1. Initialize LLM
llm = ChatGoogleGenerativeAI(
    model=settings.MODEL_NAME,
    google_api_key=settings.GOOGLE_API_KEY,
    temperature=settings.TEMPERATURE
)

# 2. Load tools
tools = get_tools()
print(f"✅ Loaded {len(tools)} tools")

# 3. Create agent
agent = create_complex_langgraph_agent(
    llm=llm,
    tools=tools,
    memory_type="postgres"
)

# 4. Use agent
result = agent.invoke(
    input_text="Hello! What can you help me with?",
    thread_id="user-123"  # Unique per user
)

print(result["output"])
```

---

## 🤖 Agent Types

### 1. Simple ReAct Agent

**File**: `src/agents/simple_agent.py`

A straightforward ReAct (Reasoning + Acting) agent perfect for:
- Simple conversations
- Quick testing and debugging
- Understanding agent behavior
- Educational purposes

**Characteristics:**
- ✅ Easy to understand
- ✅ Simple workflow (think → act → observe)
- ✅ Conversation buffer memory
- ✅ Clear reasoning steps
- ✅ Fast execution

**Usage:**
```python
from src.agents.simple_agent import create_simple_react_agent

agent = create_simple_react_agent(
    llm=llm,
    tools=tools,
    memory_type="buffer",  # or "summary" or "openmemory"
    verbose=True,
    max_iterations=5
)

result = agent.invoke("Send an email to john@example.com about interview")
print(result["output"])
```

### 2. Complex LangGraph Agent

**File**: `src/agents/complex_agent.py`

Advanced multi-node graph agent for:
- Production use
- Complex workflows
- Multi-step reasoning
- Self-reflection and improvement
- Persistent memory

**Characteristics:**
- ✅ Multi-node workflow (planner → executor → tools → reflector → responder)
- ✅ Conditional routing
- ✅ Self-reflection capabilities
- ✅ PostgreSQL checkpointer for memory
- ✅ Error handling and recovery

**Usage:**
```python
from src.agents.complex_agent import create_complex_langgraph_agent

agent = create_complex_langgraph_agent(
    llm=llm,
    tools=tools,
    memory_type="postgres",  # or "sqlite" or "memory"
    max_iterations=10,
    enable_reflection=True
)

result = agent.invoke(
    input_text="Schedule an interview for tomorrow at 2pm",
    thread_id="user-456"
)

print(result["output"])
```

---

## 🏭 Factory Pattern

Use the **AgentFactory** for flexible agent creation:

```python
from src.agents.factory import AgentFactory, AgentType, MemoryType

# Create agent via factory
agent = AgentFactory.create_agent(
    agent_type=AgentType.COMPLEX_LANGGRAPH,
    llm=llm,
    tools=tools,
    memory_type=MemoryType.POSTGRES,
    agent_config={
        "max_iterations": 10,
        "enable_reflection": True
    }
)

# Get recommendations
recommended_memory = AgentFactory.get_recommended_memory(
    AgentType.COMPLEX_LANGGRAPH
)
print(recommended_memory)  # MemoryType.POSTGRES

# Get compatible memories
compatible = AgentFactory.list_compatible_memories(
    AgentType.SIMPLE_REACT
)
print(compatible)  # [BUFFER, SUMMARY, OPENMEMORY]
```

---

## 💾 Memory System

### Thread-Based Isolation

Each user gets a unique `thread_id` for conversation memory:

```python
# User 1
result1 = agent.invoke(
    input_text="My name is Alice",
    thread_id="user-001"
)

# User 2 (different memory)
result2 = agent.invoke(
    input_text="My name is Bob",
    thread_id="user-002"
)

# User 1 continues (remembers Alice)
result3 = agent.invoke(
    input_text="What is my name?",
    thread_id="user-001"
)
# Result: "Your name is Alice"
```

### Memory Types

| Type | Description | Use Case |
|------|-------------|----------|
| **BUFFER** | Full conversation history | Simple chats, testing |
| **SUMMARY** | Summarized conversation | Long conversations, token efficiency |
| **POSTGRES** | Persistent database storage | Production, multi-user |
| **SQLITE** | Local file storage | Development, single-user |
| **MEMORY_SAVER** | In-memory (not persistent) | Temporary sessions |
| **OPENMEMORY** | Self-hosted AI memory | Advanced semantic search |

---

## 🛠️ Available Tools

The agent comes with **8 specialized tools** for HR tasks:

### 📧 Gmail Tool
**Purpose**: Email management and communication

**Operations**:
- `send_email` - Send emails to candidates
- `get_emails` - Retrieve recent emails
- `read_email` - Read specific email by ID
- `reply_email` - Reply to email threads
- `search_emails` - Search inbox with queries

**Usage Example**:
```python
# Agent will use this tool when you say:
"Send an interview invitation to candidate@example.com"
"Email the scheduling team about tomorrow's interviews"
"Search for emails from recruitment agencies"
```

### 📅 Calendar Tool
**Purpose**: Interview and meeting scheduling

**Operations**:
- `create_event` - Schedule interviews
- `list_events` - View upcoming events
- `update_event` - Modify appointments
- `delete_event` - Cancel meetings
- `check_availability` - Find free slots

**Usage Example**:
```python
# Agent will use this when you say:
"Schedule an interview for tomorrow at 2pm"
"What meetings do I have this week?"
"Cancel Friday's interview"
```

### 📊 CV Sheet Manager
**Purpose**: Candidate data management in Google Sheets

**Operations**:
- `read_all_rows` - Get all candidates
- `append_rows` - Add new candidates
- `update_row` - Modify candidate data
- `delete_row` - Remove candidates
- `search_rows` - Find candidates by criteria
- `get_row_count` - Count total candidates
- `clear_sheet` - Clear all data

**Usage Example**:
```python
# Agent will use this when you say:
"Add this candidate to the Excel sheet"
"Find all Python developers with 5+ years experience"
"How many candidates do we have?"
```

### 📄 CV Processor
**Purpose**: Extract data from CVs in Google Drive

**Operations**:
- `process_cvs` - Extract data from CV files
- Parse name, contact, experience, skills
- Auto-populate Google Sheet

**Usage Example**:
```python
# Agent will use this when you say:
"Process all CVs from the Google Drive folder"
"Extract data from these 20 CVs"
```

### 👥 Candidate Search & Ranking
**Purpose**: Intelligent candidate matching

**Operations**:
- `search_candidates` - Find candidates
- `rank_candidates` - Score by job match
- `filter_candidates` - Apply criteria

**Usage Example**:
```python
# Agent will use this when you say:
"Find the best candidates for the Senior Developer role"
"Rank these 50 candidates by Python experience"
```

### 🗂️ Sheet Management
**Purpose**: Google Sheets creation and lookup

**Operations**:
- `search_create_sheet` - Find or create sheets
- Returns `sheet_id` for other operations

**Usage Example**:
```python
# Agent will use this when you say:
"Create a new sheet for Q1 candidates"
"Find the CV data sheet"
```

### 🕐 DateTime Tool
**Purpose**: Time operations and scheduling

**Operations**:
- `get_current` - Get current date/time
- `parse_datetime` - Parse date strings
- `convert_timezone` - Timezone conversions
- `calculate_duration` - Time differences

**Usage Example**:
```python
# Agent will use this when you say:
"What time is it now?"
"Schedule for 2 hours from now"
"Convert 3pm EST to PST"
```

### 🎥 Webex Tool
**Purpose**: Video conference management

**Operations**:
- `create_meeting` - Schedule video interviews
- `list_meetings` - View all meetings
- `get_meeting` - Get meeting details
- `update_meeting` - Modify meetings
- `delete_meeting` - Cancel meetings

**Usage Example**:
```python
# Agent will use this when you say:
"Create a Webex meeting for the interview"
"Email the meeting link to the candidate"
"List all scheduled meetings"
```

---

## 🔌 Connecting to Gmail

### Prerequisites

1. **Google Cloud Project**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing

2. **Enable APIs**
   - Gmail API
   - Google Drive API
   - Google Calendar API
   - Google Sheets API

3. **Create OAuth 2.0 Credentials**
   - Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client ID"
   - Choose "Desktop Application"
   - Download JSON file
   - Save as `client_secret.json` in project root

### Setup Steps

1. **Configure OAuth in settings**
   ```python
   # src/config/settings.py
   GOOGLE_APPLICATION_CREDENTIALS = "client_secret.json"
   OAUTH_CREDENTIALS_FILE = "client_secret.json"
   ```

2. **Run OAuth Setup**
   ```bash
   python3 -c "
   from src.integrations.google import GoogleServices
   gs = GoogleServices()
   print('✅ Authentication complete!')
   "
   ```

3. **First Authentication**
   - Opens browser window
   - Sign in to Google account
   - Grant permissions
   - Token saved to `token.pickle`

4. **Verify Gmail Access**
   ```bash
   python3 -c "
   from src.agents.tool_factory import get_tools
   tools = get_tools()
   gmail_tool = [t for t in tools if t.name == 'gmail'][0]
   result = gmail_tool.run({
       'operation': 'search_emails',
       'query': 'is:unread',
       'max_results': 5
   })
   print('✅ Gmail working!' if result else '❌ Gmail failed')
   "
   ```

### Gmail Usage Examples

**Send Email**:
```python
# Agent will handle this automatically:
"Send an email to john.doe@company.com with subject 'Interview Invitation' and body 'Dear John, we'd like to invite you for an interview...'"
```

**Check Inbox**:
```python
# Agent will handle this automatically:
"Show me unread emails from the last week"
"Search for emails about 'interview scheduling'"
```

---

## 🎥 Connecting to Webex

### Prerequisites

1. **Webex Developer Account**
   - Go to [Webex Developer Portal](https://developer.webex.com/)
   - Create app or use existing

2. **Get Credentials**
   - CLIENT_ID
   - CLIENT_SECRET

### Setup Steps

1. **Configure Webex**
   ```bash
   # .env file
   WEBEX_CLIENT_ID=your_client_id
   WEBEX_CLIENT_SECRET=your_client_secret
   WEBEX_ACCESS_TOKEN=your_access_token  # Optional: direct token
   ```

2. **Initialize Webex Service**
   ```python
   from src.integrations.webex_sdk import WebexClient

   webex = WebexClient()
   print("✅ Webex initialized!")
   ```

3. **Test Connection**
   ```bash
   python3 -c "
   from src.agents.tool_factory import get_tools
   tools = get_tools()
   webex_tool = [t for t in tools if t.name == 'webex'][0]
   result = webex_tool.run({'operation': 'list_meetings'})
   print('✅ Webex working!' if result else '❌ Webex failed')
   "
   ```

### Webex Usage Examples

**Create Meeting**:
```python
# Agent will handle this automatically:
"Create a Webex meeting for tomorrow at 2pm with candidate@email.com"
"Schedule a 30-minute interview for the Senior Developer position"
```

**Manage Meetings**:
```python
# Agent will handle this automatically:
"List all meetings for this week"
"Cancel Friday's 3pm meeting"
"Email the meeting link to participants"
```

---

## 📊 Database Integration

### PostgreSQL Checkpointer

The complex agent uses **LangGraph PostgreSQL checkpointer** for memory:

```python
# Automatic - created when agent is instantiated
agent = create_complex_langgraph_agent(
    llm=llm,
    tools=tools,
    memory_type="postgres"  # Uses checkpointer
)

# Manual checkpointer (if needed)
from src.memory.postgres import get_checkpointer

checkpointer = get_checkpointer()
```

**Database Tables**:
- `checkpoints` - Conversation state
- `checkpoint_blobs` - Message data
- `checkpoint_writes` - Write operations

**Verify Setup**:
```bash
python3 -c "
import psycopg
from src.config import settings
conn = psycopg.connect(settings.DATABASE_URL)
cur = conn.cursor()
cur.execute('SELECT COUNT(*) FROM checkpoints')
count = cur.fetchone()[0]
print(f'✅ Checkpoints: {count}')
conn.close()
"
```

---

## 🧪 Testing Your Agents

### Interactive Testing with Notebooks

```bash
# Launch Jupyter
jupyter notebook tests/notebooks/

# Test notebooks:
# 01_tools_testing.ipynb - Test all tools individually
# 02_agents_testing.ipynb - Test agent workflows
# 03_custom_agent_tutorial.ipynb - Build custom agents
# 04_mcp_integration.ipynb - MCP protocol
# 07_complete_system_test.ipynb - Full system test
```

### Command Line Testing

```python
# Test 1: Simple agent creation
from src.agents.simple_agent import create_simple_react_agent
from src.config import settings
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.7)
agent = create_simple_react_agent(llm=llm, tools=[], memory_type="buffer")
result = agent.invoke("Hello!")
print(result["output"])
```

```python
# Test 2: Complex agent with memory
from src.agents.complex_agent import create_complex_langgraph_agent

agent = create_complex_langgraph_agent(llm=llm, tools=[], memory_type="postgres")
result = agent.invoke("My name is Alice", thread_id="test-1")
result = agent.invoke("What is my name?", thread_id="test-1")
print(result["output"])  # Should say "Alice"
```

### Debug Mode

```python
# Enable verbose mode
agent = create_complex_langgraph_agent(
    llm=llm,
    tools=tools,
    memory_type="postgres",
    verbose=True  # Shows detailed execution
)

result = agent.invoke("What can you do?", thread_id="debug-1")
```

---

## 🏗️ Custom Agent Development

### Extend Simple Agent

```python
from src.agents.simple_agent import SimpleReActAgent

class CustomAgent(SimpleReActAgent):
    def custom_method(self):
        # Add your custom functionality
        pass

# Create with custom settings
agent = CustomAgent(
    llm=llm,
    tools=tools,
    max_iterations=10,  # Custom parameter
    verbose=True
)
```

### Extend Complex Agent

```python
from src.agents.complex_agent import ComplexLangGraphAgent

class CustomLangGraphAgent(ComplexLangGraphAgent):
    def _custom_node(self, state):
        # Add custom node to graph
        return {"custom": "data"}

# Or modify existing graph
agent = ComplexLangGraphAgent(llm=llm, tools=tools)
agent.graph = agent._build_custom_graph()
```

---

## 🔧 Configuration

### Agent Configuration Options

**Simple Agent**:
```python
{
    "verbose": True,              # Show reasoning steps
    "max_iterations": 5,          # Maximum thought-action cycles
    "max_execution_time": None,   # Max time in seconds
}
```

**Complex Agent**:
```python
{
    "verbose": True,              # Show execution details
    "max_iterations": 10,         # Maximum loops
    "enable_reflection": True,    # Enable self-reflection node
}
```

### Tool Configuration

Edit `config/tools.yaml`:

```yaml
tools:
  # Enable/disable tools
  gmail:
    enabled: true
    provider: "internal_mcp"  # internal_mcp, mcp_client, or auto

  calendar:
    enabled: true
    provider: "mcp_client"

  # Custom tool
  my_tool:
    enabled: true
    provider: "internal_mcp"
    custom_option: "value"
```

---

## 📝 API Reference

### ComplexLangGraphAgent.invoke()

```python
def invoke(
    self,
    input_text: str,
    thread_id: str = "default"
) -> Dict[str, Any]:
    """
    Process user input through the agent workflow.

    Args:
        input_text: User message
        thread_id: Unique ID for conversation memory

    Returns:
        {
            "output": str,           # Final response
            "messages": List,        # All messages in conversation
            "iterations": int,       # Number of iterations
            "reflection": str,       # Self-reflection (if enabled)
            "success": bool          # Success status
        }
    """
```

### SimpleReActAgent.invoke()

```python
def invoke(self, input_text: str) -> Dict[str, Any]:
    """
    Process input through ReAct workflow.

    Args:
        input_text: User message

    Returns:
        {
            "output": str,                  # Final response
            "intermediate_steps": List,     # ReAct steps
            "success": bool                 # Success status
        }
    """
```

---

## 🚨 Troubleshooting

### Issue: "Tool not found"

**Solution**:
```bash
# Check available tools
python3 -c "
from src.agents.tool_factory import get_tools
tools = get_tools()
print(f'Loaded {len(tools)} tools')
for t in tools:
    print(f'  - {t.name}')
"

# Verify tools.yaml is correct
cat config/tools.yaml
```

### Issue: "Memory not working"

**Solution**:
```bash
# Check database connection
python3 -c "
import psycopg
from src.config import settings
try:
    conn = psycopg.connect(settings.DATABASE_URL)
    cur = conn.cursor()
    cur.execute('SELECT table_name FROM information_schema.tables WHERE table_name LIKE \"checkpoint%\"')
    print([r[0] for r in cur.fetchall()])
    conn.close()
    print('✅ Database OK')
except Exception as e:
    print(f'❌ Database error: {e}')
"
```

### Issue: "Gmail API not working"

**Solution**:
```bash
# Refresh OAuth token
rm token.pickle
python3 -c "from src.integrations.google import GoogleServices; GoogleServices()"

# Check scopes in google.py
grep "SCOPES" src/integrations/google.py
# Should include: 'https://mail.google.com/' for full Gmail access
```

### Issue: "Complex agent returns errors"

**Solution**:
```python
# Enable verbose mode
agent = create_complex_langgraph_agent(
    llm=llm,
    tools=tools,
    memory_type="postgres",
    verbose=True
)

# Check result details
result = agent.invoke(input_text, thread_id="test")
print(f"Success: {result.get('success')}")
print(f"Output: {result.get('output')}")
print(f"Iterations: {result.get('iterations')}")
if not result.get('success'):
    print(f"Error: {result.get('error')}")
```

---

## 📚 Additional Resources

### Documentation Files

- **Main README**: `/README.md` - Project overview
- **Config Guide**: `/config/README.md` - Tool configuration
- **Docs Index**: `/docs/DOCS_INDEX.md` - Complete documentation
- **Troubleshooting**: `/docs/TROUBLESHOOTING.md` - Common issues
- **How to Add Tools**: `/docs/HOW_TO_ADD_TOOLS.md` - Developer guide

### Testing Resources

- **Notebooks**: `/tests/notebooks/` - Interactive testing
- **Test Scripts**: `/tests/` - Automated tests

### Example Files

- **Message Handler**: `/src/api/handlers/message_handler.py` - WhatsApp integration
- **Factory**: `/src/agents/factory.py` - Agent creation patterns
- **Tools**: `/src/tools/` - Tool implementations

---

## 🎓 Learning Path

1. **Start Here**
   - Read this README
   - Run notebook `02_agents_testing.ipynb`
   - Test simple agent

2. **Understanding Tools**
   - Run notebook `01_tools_testing.ipynb`
   - Learn each tool individually
   - Understand Gmail/Calendar integration

3. **Custom Development**
   - Run notebook `03_custom_agent_tutorial.ipynb`
   - Learn to extend agents
   - Create custom tools

4. **Production Setup**
   - Configure PostgreSQL checkpointer
   - Setup Gmail OAuth
   - Test with WhatsApp integration

5. **Advanced Topics**
   - MCP protocol (`04_mcp_integration.ipynb`)
   - Memory system (`06_agents_and_memory_testing.ipynb`)
   - Full system test (`07_complete_system_test.ipynb`)

---

## ✅ Checklist

Before going to production:

- [ ] PostgreSQL database configured
- [ ] Gmail OAuth credentials set up
- [ ] Tools enabled in `config/tools.yaml`
- [ ] Webex credentials configured (if using)
- [ ] Google Drive folder IDs set (for CV processing)
- [ ] All notebooks tested successfully
- [ ] Agent memory working (test with thread_id)
- [ ] WhatsApp integration tested
- [ ] Monitoring dashboard accessible

---

## 💡 Tips & Best Practices

1. **Use Thread IDs Wisely**
   - One thread_id per user
   - Use phone number or unique identifier
   - Don't reuse thread_ids across users

2. **Tool Selection**
   - Keep tools.yaml minimal (only enabled tools you need)
   - Use `internal_mcp` when possible (faster)
   - Use `mcp_client` for official external tools

3. **Memory Management**
   - Use `postgres` for production
   - Use `buffer` for testing
   - Use `sqlite` for development

4. **Error Handling**
   - Always check `result['success']`
   - Enable verbose mode during development
   - Log errors for debugging

5. **Performance**
   - Limit `max_iterations` to prevent infinite loops
   - Use reflection only when needed
   - Monitor memory usage in database

---

**For questions or issues:**
- 📖 Check `/docs/TROUBLESHOOTING.md`
- 🧪 Run test notebooks in `/tests/notebooks/`
- 📝 Review example code in `/src/agents/`
- 🚀 Start with simple agent, then complex

---

**Happy building! 🎉**
