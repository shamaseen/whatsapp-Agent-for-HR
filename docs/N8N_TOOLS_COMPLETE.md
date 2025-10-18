# Complete n8n Tools Inventory & MCP Implementation Plan

## 📊 Full Tool Comparison

### ✅ **Tools Already Implemented (Python)**
| Tool | n8n | Python | MCP Ready |
|------|-----|--------|-----------|
| DateTime | ✅ Date & Time node | ✅ `tools/datetime_tools.py` | ⏳ Need MCP |

### ❌ **Tools Missing (Need Implementation)**

#### 1. **MCP Clients (n8n has, Python doesn't)**
| Tool | n8n Endpoint | Status |
|------|--------------|--------|
| MCP Sequential Thinking | `/mcp/ae76bcd5...` | ✅ Created `mcp/thinking.py` |
| CV Sheet Manager MCP | `/mcp/9e10ec8f...` | 🚧 Creating now |
| Gmail MCP | `/mcp/7a1acee6...` | ⏳ Pending |
| Calendar MCP | `/mcp/c360a222...` | ⏳ Pending |
| Webex MCP | `/mcp/93706721...` | ⏳ Pending |

#### 2. **Webhook Tools (n8n has, Python has basic versions)**
| Tool | n8n Webhook | Python Version | MCP Needed |
|------|-------------|----------------|------------|
| Search Candidates | `/webhook/search-candidates` | ✅ `tools/cv_tools.py:search_candidates` | ✅ Convert to MCP |
| CV Summarize/Process | `/webhook/e99a90c4...` | ✅ `tools/cv_tools.py:process_cvs` | ✅ Convert to MCP |
| Search & Create Sheet | `/webhook/98f286ad...` | ✅ `tools/cv_tools.py:search_create_sheet` | ✅ Convert to MCP |

### 🔧 **Complete Tool List from n8n**

#### **Agent Tools (Connected to AI Agent):**
1. ✅ **Date & Time** - Get current date/time
2. ⏳ **Top Person** - HTTP tool to search candidates
3. ⏳ **CV Summarize** - HTTP tool to process CVs
4. ⏳ **Search and Create CV Sheet** - HTTP tool to manage sheets
5. ⏳ **Webex MCP Client** - Schedule meetings
6. ⏳ **Gmail MCP Client** - Send emails
7. ⏳ **Calendar MCP Client** - Schedule events
8. ⏳ **CV Sheet Manager MCP** - Advanced sheet operations
9. ✅ **MCP Sequential Thinking** - AI reasoning (CREATED!)

#### **Webhook Services (CV Processing):**
1. `/webhook/e99a90c4-0696-46da-b729-92596d37a6c2` - **Process CVs**
   - Lists files from Google Drive
   - Extracts PDF text
   - AI summarizes CV
   - Saves to Google Sheets

2. `/webhook/search-candidates` - **Search Candidates**
   - Reads all candidates from sheet
   - AI ranks by job position
   - Returns top N matches

3. `/webhook/98f286ad-9135-4b1d-9147-d23942408d15` - **Create/Find Sheet**
   - Searches for existing sheet
   - Creates new if not found
   - Returns sheet_id

## 🎯 Complete MCP Implementation Plan

### Phase 1: Core MCP Tools ✅
- [x] MCP base protocol (`list_tools`, `execute_tool`)
- [x] Tool registry system
- [x] Sequential Thinking MCP

### Phase 2: CV Management MCP Tools 🚧
- [ ] **CV Sheet Manager MCP** - Full CRUD operations on sheets
  - `read_sheet`: Get all rows from sheet
  - `append_rows`: Add new CV data
  - `update_row`: Modify existing data
  - `delete_row`: Remove entries
  - `search_rows`: Query candidates

- [ ] **CV Processing Tool** (from `process_cvs`)
  - Download PDFs from Google Drive
  - Extract text using PyMuPDF
  - AI extraction of CV fields
  - Deduplication
  - Save to sheet

- [ ] **Candidate Search Tool** (from `search_candidates`)
  - Read all candidates
  - AI ranking by job position
  - Match score calculation
  - Return top N

- [ ] **Sheet Lookup Tool** (from `search_create_sheet`)
  - Search by name
  - Create if not exists
  - Return sheet_id

### Phase 3: Communication MCP Tools
- [ ] **Gmail MCP**
  - `send_email`: Send emails
  - `list_emails`: Get inbox (future)
  - `read_email`: Read message (future)
  - `search_emails`: Query (future)

- [ ] **Calendar MCP**
  - `create_event`: Schedule meetings
  - `list_events`: Get calendar
  - `update_event`: Modify
  - `delete_event`: Cancel

- [ ] **Webex MCP**
  - `create_meeting`: Schedule Webex
  - `get_meeting`: Get details
  - `update_meeting`: Modify
  - `delete_meeting`: Cancel

### Phase 4: Utility MCP Tools
- [ ] **DateTime MCP**
  - `get_current_datetime`: Current time
  - `convert_timezone`: TZ conversion
  - `parse_datetime`: Parse strings
  - `calculate_duration`: Time math

## 📋 System Prompt Updates (from n8n)

Key sections to add:
1. **Always call `list_tools` first**
2. **Use Sequential Thinking for complex tasks**
3. **All tool calls via `execute_tool`**
4. **Automatic context extraction**:
   - Phone number → Sheet name
   - Sender info → Identifiers
5. **Tool verification workflow**
6. **Error handling patterns**

## 🏗️ Architecture

```
┌──────────────────────────────────────────────┐
│          LangGraph Agent                     │
│    (MCP-aware system prompt)                 │
└─────────────────┬────────────────────────────┘
                  │
        ┌─────────┴─────────┐
        │                   │
        ▼                   ▼
   list_tools()        execute_tool()
        │                   │
        └─────────┬─────────┘
                  │
         ┌────────┴────────┐
         │  MCP Registry   │
         └────────┬────────┘
                  │
    ┌─────────────┼─────────────┬──────────────┐
    │             │             │              │
    ▼             ▼             ▼              ▼
Thinking      CV Tools    Communication   Utilities
  MCP           MCP            MCP           MCP
```

## 🔄 Migration Strategy

### Approach: **Incremental MCP Adoption**

1. **Keep existing tools working** ✅
2. **Create MCP versions alongside** 🚧
3. **Register both in agent** ⏳
4. **Test MCP versions** ⏳
5. **Deprecate old versions** ⏳

### Benefits:
- No breaking changes
- Easy rollback
- Gradual migration
- Test in parallel

## 📝 Implementation Order

1. ✅ MCP base + Sequential Thinking
2. 🚧 CV Sheet Manager MCP (most complex)
3. ⏳ Gmail MCP (simple, high value)
4. ⏳ Calendar MCP (simple, high value)
5. ⏳ Webex MCP (simple, optional)
6. ⏳ DateTime MCP (simple utility)
7. ⏳ Migrate CV tools to MCP
8. ⏳ Update agent configuration
9. ⏳ Update system prompt
10. ⏳ Integration testing
11. ⏳ Update test notebooks
12. ⏳ Documentation

## 🎉 Expected Outcome

After full MCP implementation:
- **9+ MCP tools** available
- **Standardized interface** across all tools
- **Better tool discovery** via `list_tools`
- **AI reasoning** before complex actions
- **Error handling** built into protocol
- **Easier extensibility** for new tools
- **Matches n8n functionality** 1:1
