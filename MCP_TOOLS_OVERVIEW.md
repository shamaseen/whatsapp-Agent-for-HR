# MCP Tools Overview

Complete reference for all MCP (Model Context Protocol) tools available in the WhatsApp HR Assistant.

## 📁 File Organization

All MCP tools are organized in separate files under `/mcp` directory for easy monitoring and maintenance:

```
mcp/
├── base.py                 # Base MCP classes and registry
├── thinking.py             # Sequential thinking tool
├── gmail_mcp.py           # Gmail operations
├── calendar_mcp.py        # Calendar operations
├── cv_manager.py          # CV sheet management
├── cv_tools_mcp.py        # CV processing tools
├── datetime_mcp.py        # Date/time operations
├── webex_mcp.py           # Webex meeting operations
└── __init__.py            # Module exports
```

---

## 🔧 Available MCP Tools

### 1. **Gmail MCP** (`gmail_mcp.py`)
**Tool Name:** `gmail`

**Operations:**
| Operation | Description | Required Parameters |
|-----------|-------------|-------------------|
| `send_email` | Send an email to recipients | `to_email`, `subject`, `body` |
| `get_emails` | Get recent emails from inbox | `max_results` (optional, default: 10) |
| `read_email` | Read a specific email by ID | `message_id` |
| `reply_email` | Reply to an email thread | `message_id`, `body` |
| `search_emails` | Search emails by query | `query`, `max_results` (optional) |

**Example Usage:**
```python
# Send email
execute_tool(tool_name="gmail", parameters={
    "operation": "send_email",
    "to_email": "candidate@example.com",
    "subject": "Interview Invitation",
    "body": "Dear candidate, we would like to invite you..."
})

# Get recent emails
execute_tool(tool_name="gmail", parameters={
    "operation": "get_emails",
    "max_results": 5
})

# Reply to email
execute_tool(tool_name="gmail", parameters={
    "operation": "reply_email",
    "message_id": "abc123",
    "body": "Thank you for your application..."
})
```

---

### 2. **Calendar MCP** (`calendar_mcp.py`)
**Tool Name:** `calendar`

**Operations:**
| Operation | Description | Required Parameters |
|-----------|-------------|-------------------|
| `create_event` | Schedule a new calendar event | `summary`, `start_time`, `end_time` |
| `list_events` | List upcoming events | `max_results` (optional, default: 10) |
| `get_event` | Get details of specific event | `event_id` |
| `update_event` | Modify existing event | `event_id`, + any fields to update |
| `delete_event` | Cancel/delete an event | `event_id` |

**Example Usage:**
```python
# Create event
execute_tool(tool_name="calendar", parameters={
    "operation": "create_event",
    "summary": "Interview with John Doe",
    "start_time": "2025-10-20T14:00:00Z",
    "end_time": "2025-10-20T15:00:00Z",
    "attendees": ["john@example.com"],
    "description": "Technical interview for Senior Python Developer position"
})

# Update event
execute_tool(tool_name="calendar", parameters={
    "operation": "update_event",
    "event_id": "event123",
    "start_time": "2025-10-20T15:00:00Z"
})

# Delete event
execute_tool(tool_name="calendar", parameters={
    "operation": "delete_event",
    "event_id": "event123"
})
```

---

### 3. **CV Sheet Manager MCP** (`cv_manager.py`)
**Tool Name:** `cv_sheet_manager`

**Operations:**
| Operation | Description | Required Parameters |
|-----------|-------------|-------------------|
| `read_all_rows` | Get all candidate rows from sheet | `sheet_id` |
| `append_rows` | Add new CV data to sheet | `sheet_id`, `data` |
| `update_row` | Modify existing row by index | `sheet_id`, `row_index`, `data` |
| `delete_row` | Remove a row by index | `sheet_id`, `row_index` |
| `search_rows` | Query candidates by criteria | `sheet_id`, `search_criteria` |
| `get_row_count` | Get number of rows in sheet | `sheet_id` |
| `clear_sheet` | Clear all data (keeps headers) | `sheet_id` |

**Example Usage:**
```python
# Read all candidates
execute_tool(tool_name="cv_sheet_manager", parameters={
    "operation": "read_all_rows",
    "sheet_id": "abc123xyz"
})

# Clear sheet
execute_tool(tool_name="cv_sheet_manager", parameters={
    "operation": "clear_sheet",
    "sheet_id": "abc123xyz"
})

# Search candidates
execute_tool(tool_name="cv_sheet_manager", parameters={
    "operation": "search_rows",
    "sheet_id": "abc123xyz",
    "search_criteria": {"skills": "Python", "experienceYears": "5"}
})
```

---

### 4. **CV Processing Tools** (`cv_tools_mcp.py`)

#### 4a. **Search/Create Sheet**
**Tool Name:** `search_create_sheet`

Find or create a Google Sheet by name (typically uses phone number).

```python
execute_tool(tool_name="search_create_sheet", parameters={
    "sheet_name": "962776241974"
})
```

#### 4b. **Process CVs**
**Tool Name:** `process_cvs`

Extract CV data from Google Drive and store in sheet.

```python
execute_tool(tool_name="process_cvs", parameters={
    "sheet_id": "abc123xyz"
})
```

#### 4c. **Search Candidates**
**Tool Name:** `search_candidates`

Search and rank candidates for a job position.

```python
execute_tool(tool_name="search_candidates", parameters={
    "sheet_id": "abc123xyz",
    "job_position": "Senior Python Developer"
})
```

---

### 5. **DateTime MCP** (`datetime_mcp.py`)
**Tool Name:** `datetime`

**Operations:**
| Operation | Description | Parameters |
|-----------|-------------|-----------|
| `get_current` | Get current date/time | None |
| `add_time` | Add duration to time | `datetime`, `hours`, `minutes` |
| `format_datetime` | Format datetime string | `datetime`, `format` |

**Example Usage:**
```python
# Get current time
execute_tool(tool_name="datetime", parameters={
    "operation": "get_current"
})

# Add time
execute_tool(tool_name="datetime", parameters={
    "operation": "add_time",
    "datetime": "2025-10-20T14:00:00Z",
    "hours": 2
})
```

---

### 6. **Webex MCP** (`webex_mcp.py`)
**Tool Name:** `webex`

**Operations:**
| Operation | Description | Required Parameters |
|-----------|-------------|-------------------|
| `create_meeting` | Schedule a Webex meeting | `title`, `start`, `end` |
| `get_meeting` | Get meeting details | `meeting_id` |
| `update_meeting` | Modify meeting | `meeting_id`, + fields to update |
| `delete_meeting` | Cancel meeting | `meeting_id` |

---

### 7. **Sequential Thinking** (`thinking.py`)
**Tool Name:** `sequential_thinking`

Plan complex tasks step-by-step before execution.

```python
execute_tool(tool_name="sequential_thinking", parameters={
    "task": "Process CVs and schedule interviews",
    "context": "User phone: 962776241974"
})
```

---

## 🎯 Benefits of Separation

### Easy Monitoring
Each MCP tool is in its own file, making it easy to:
- Track which tool is being used
- Debug specific tool issues
- Monitor performance per tool
- Update tools independently

### Clear Organization
```
├── Communication Tools
│   ├── gmail_mcp.py       (Email operations)
│   ├── webex_mcp.py       (Video meetings)
│
├── Data Management Tools
│   ├── cv_manager.py      (Sheet CRUD)
│   ├── cv_tools_mcp.py    (CV processing)
│
├── Scheduling Tools
│   ├── calendar_mcp.py    (Calendar CRUD)
│   ├── datetime_mcp.py    (Time operations)
│
└── Utility Tools
    ├── thinking.py        (Planning)
    └── base.py           (Core infrastructure)
```

### Logging & Debugging
Each tool execution is logged separately in the dashboard:
- Tool name
- Parameters used
- Execution time
- Success/failure status
- Results returned

---

## 📊 Dashboard Integration

All tool executions are tracked in the monitoring dashboard at `http://localhost:8000`:

**Metrics shown:**
- Most used tools
- Tool success rates
- Average execution time per tool
- Tool call sequences
- Error tracking per tool

**Detailed view includes:**
- Tool parameters
- Tool results
- Execution order
- Error messages (if any)

---

## 🔄 Workflow Examples

### Complete Recruitment Flow

```python
# 1. Create/find sheet
execute_tool(tool_name="search_create_sheet", parameters={
    "sheet_name": "962776241974"
})
# Returns: {"sheet_id": "abc123"}

# 2. Process CVs
execute_tool(tool_name="process_cvs", parameters={
    "sheet_id": "abc123"
})

# 3. Search candidates
execute_tool(tool_name="search_candidates", parameters={
    "sheet_id": "abc123",
    "job_position": "Backend Developer"
})
# Returns top 5 ranked candidates

# 4. Schedule interview
execute_tool(tool_name="calendar", parameters={
    "operation": "create_event",
    "summary": "Interview - John Doe",
    "start_time": "2025-10-20T14:00:00Z",
    "end_time": "2025-10-20T15:00:00Z",
    "attendees": ["john@example.com"]
})

# 5. Send invitation email
execute_tool(tool_name="gmail", parameters={
    "operation": "send_email",
    "to_email": "john@example.com",
    "subject": "Interview Invitation",
    "body": "Dear John, you are invited to an interview..."
})
```

---

## 🎓 Best Practices

1. **Always use `search_create_sheet` first** before CV operations
2. **Use phone number as sheet_name** for automatic identification
3. **Check email responses** with `get_emails` before sending follow-ups
4. **Use `sequential_thinking`** for complex multi-step workflows
5. **Verify calendar events** with `list_events` before creating new ones
6. **Clear sheets** with `clear_sheet` instead of manual deletion
7. **Monitor tool execution** in dashboard for debugging

---

## 📝 Adding New Tools

To add a new MCP tool:

1. Create new file in `/mcp` directory (e.g., `new_tool_mcp.py`)
2. Extend `MCPTool` base class
3. Implement required methods:
   - `get_name()`
   - `get_description()`
   - `get_input_schema()`
   - `execute()`
4. Register in `mcp/__init__.py`
5. Update `agents/prompts.py` with tool description
6. Test in notebooks

---

## 🔍 Troubleshooting

**Tool not found error:**
- Check tool is registered in `mcp_registry`
- Verify tool name matches exactly

**Permission denied:**
- Check Google OAuth scopes
- Verify service account permissions

**Tool timeout:**
- Check network connectivity
- Verify API quotas not exceeded
- Review dashboard logs for details

---

## 📚 Further Reading

- [Google Calendar API](https://developers.google.com/calendar/api)
- [Gmail API](https://developers.google.com/gmail/api)
- [Google Sheets API](https://developers.google.com/sheets/api)
- [LangGraph Documentation](https://python.langchain.com/docs/langgraph)
