# Tool Modes Comparison Guide

Complete comparison of the three tool execution modes available in the WhatsApp HR Assistant.

## 📋 Quick Reference

| Feature | MCP (Local) | MCP Client | Direct (Legacy) |
|---------|-------------|------------|-----------------|
| **Configuration** | `TOOL_MODE=mcp` | `TOOL_MODE=mcp_client` | `TOOL_MODE=direct` |
| **Execution** | Local MCP tools | External MCP server | Local LangChain tools |
| **Protocol** | MCP | MCP over HTTP/stdio | LangChain |
| **Tool Count** | 9+ tools | 2 client tools | 8 tools |
| **Setup Complexity** | Low | Medium | Low |
| **External Dependencies** | None | MCP server required | None |
| **Scalability** | Single process | Distributed | Single process |
| **Best For** | Production | Microservices | Legacy compatibility |

---

## 🔧 Mode 1: MCP (Local) - **Recommended**

### Overview
Uses local MCP-compatible tool implementations with unified `execute_tool` interface.

### Configuration
```bash
TOOL_MODE=mcp
```

### Available Tools
1. **sequential_thinking** - AI planning and reasoning
2. **cv_sheet_manager** - CV sheet CRUD (7 operations)
3. **gmail** - Email operations (5 operations)
4. **calendar** - Calendar CRUD (5 operations)
5. **webex** - Webex meetings (4 operations)
6. **datetime** - Time utilities (3 operations)
7. **process_cvs** - CV extraction from Drive
8. **search_candidates** - Candidate ranking
9. **search_create_sheet** - Sheet management

### Advantages
- ✅ Clean, standardized interface
- ✅ All tools in one place
- ✅ Easy debugging and monitoring
- ✅ No external dependencies
- ✅ Full control over execution
- ✅ Best performance

### Disadvantages
- ❌ Single process (no distribution)
- ❌ All tools run locally

### Use Cases
- Production deployments
- Single-server applications
- When you need full control
- Standard HR automation workflows

### Example
```python
# Agent uses execute_tool to call any MCP tool
execute_tool(
    tool_name="gmail",
    parameters={
        "operation": "send_email",
        "to_email": "candidate@example.com",
        "subject": "Interview",
        "body": "Hello!"
    }
)
```

---

## 🌐 Mode 2: MCP Client - **Advanced**

### Overview
Connects to external MCP servers via HTTP/SSE or stdio transport.

### Configuration
```bash
TOOL_MODE=mcp_client
MCP_SERVER_URL=http://localhost:3000
MCP_SERVER_TRANSPORT=sse  # or "stdio"
```

### Available Tools
1. **mcp_client_list_tools** - Discover tools from MCP server
2. **mcp_client_execute_tool** - Execute tools on MCP server

### Advantages
- ✅ Distributed architecture
- ✅ Service isolation
- ✅ Independent scaling
- ✅ Connect to external services
- ✅ Dynamic tool discovery
- ✅ Supports multiple servers

### Disadvantages
- ❌ Requires external MCP server
- ❌ Network overhead
- ❌ More complex setup
- ❌ Additional point of failure

### Use Cases
- Microservices architecture
- Distributed systems
- When tools run on different servers
- Integration with third-party MCP services
- High-load scenarios requiring scaling

### Example
```python
# 1. Discover available tools
tools = mcp_client_list_tools()

# 2. Execute tool on remote server
result = mcp_client_execute_tool(
    tool_name="gmail",
    parameters={
        "operation": "send_email",
        "to_email": "candidate@example.com",
        "subject": "Interview",
        "body": "Hello!"
    }
)
```

### Setting up MCP Server
See [MCP_CLIENT_GUIDE.md](./MCP_CLIENT_GUIDE.md) for complete server setup instructions.

---

## 📦 Mode 3: Direct - **Legacy**

### Overview
Traditional LangChain tools without MCP protocol wrapper.

### Configuration
```bash
TOOL_MODE=direct
```

### Available Tools
1. **search_create_sheet** - Find/create CV sheet
2. **process_cvs** - Extract CV data
3. **search_candidates** - Rank candidates
4. **schedule_calendar_event** - Create calendar events
5. **send_email** - Send emails
6. **get_current_datetime** - Get current time
7. **schedule_webex_meeting** - Create Webex meetings
8. **get_webex_meeting_details** - Get meeting info

### Advantages
- ✅ No protocol overhead
- ✅ Direct execution
- ✅ Backward compatible
- ✅ Simple implementation

### Disadvantages
- ❌ Not standardized
- ❌ Harder to monitor
- ❌ Less flexible
- ❌ Legacy approach

### Use Cases
- Backward compatibility
- Simple workflows
- When MCP protocol is not needed
- Legacy integrations

### Example
```python
# Direct tool invocation
send_email(
    to_email="candidate@example.com",
    subject="Interview",
    body="Hello!"
)
```

---

## 🎯 Which Mode Should You Use?

### Choose **MCP (Local)** if:
- ✅ You're starting a new project
- ✅ You want the cleanest architecture
- ✅ All tools can run locally
- ✅ You value simplicity and performance

### Choose **MCP Client** if:
- ✅ You need distributed architecture
- ✅ Tools run on different servers
- ✅ You want to scale independently
- ✅ You're integrating with external MCP services

### Choose **Direct** if:
- ✅ You have legacy code to maintain
- ✅ You need backward compatibility
- ✅ You prefer traditional LangChain approach
- ✅ MCP protocol is unnecessary

---

## 🔄 Migration Guide

### From Direct to MCP

1. Update `.env`:
   ```bash
   TOOL_MODE=mcp
   ```

2. No code changes needed - tools are compatible

3. Test thoroughly

### From MCP to MCP Client

1. Set up MCP server (see [MCP_CLIENT_GUIDE.md](./MCP_CLIENT_GUIDE.md))

2. Update `.env`:
   ```bash
   TOOL_MODE=mcp_client
   MCP_SERVER_URL=http://your-server:3000
   MCP_SERVER_TRANSPORT=sse
   ```

3. Deploy MCP server with your tools

4. Test connectivity

### From MCP Client to MCP

1. Update `.env`:
   ```bash
   TOOL_MODE=mcp
   ```

2. Remove MCP server configuration

3. All tools now run locally

---

## 📊 Performance Comparison

### Latency

| Mode | Avg Response Time | Notes |
|------|------------------|-------|
| MCP | ~100-200ms | Direct execution |
| MCP Client | ~200-500ms | +network overhead |
| Direct | ~100-200ms | Direct execution |

### Throughput

| Mode | Concurrent Requests | Notes |
|------|-------------------|-------|
| MCP | 10-20 | Single process |
| MCP Client | 50+ | Distributed |
| Direct | 10-20 | Single process |

### Resource Usage

| Mode | CPU | Memory | Network |
|------|-----|--------|---------|
| MCP | Medium | Medium | None |
| MCP Client | Low | Low | High |
| Direct | Medium | Medium | None |

---

## 🐛 Troubleshooting

### MCP Mode Issues

**Problem:** Tool not found
```
Error: Tool 'gmail' not found in registry
```

**Solution:**
- Check tool is registered in `tool_factory.py`
- Verify MCP tools are imported correctly

### MCP Client Issues

**Problem:** Connection refused
```
Error: Failed to connect to MCP server
```

**Solution:**
- Ensure MCP server is running
- Verify `MCP_SERVER_URL` in `.env`
- Check firewall settings

### Direct Mode Issues

**Problem:** Tool import error
```
Error: cannot import name 'send_email'
```

**Solution:**
- Check tool exists in `tools/` directory
- Verify imports in `tool_factory.py`

---

## 📚 Additional Resources

- **[MCP_TOOLS_OVERVIEW.md](../MCP_TOOLS_OVERVIEW.md)** - Complete tool reference
- **[MCP_CLIENT_GUIDE.md](./MCP_CLIENT_GUIDE.md)** - MCP Client setup guide
- **[README.md](../README.md)** - Main documentation
- **[config.py](../config.py)** - Configuration reference

---

## 🎓 Best Practices

### General
1. Always test thoroughly when switching modes
2. Monitor performance and errors
3. Use appropriate mode for your architecture
4. Document your choice

### For Production
1. Use **MCP mode** for single-server deployments
2. Use **MCP Client** for distributed systems
3. Avoid **Direct mode** unless necessary

### For Development
1. Start with **MCP mode** for simplicity
2. Test **MCP Client** in staging before production
3. Use debug logging to diagnose issues

---

## 📞 Support

Need help choosing or implementing a tool mode?

- 📧 Email: support@example.com
- 🐛 Issues: [GitHub Issues](https://github.com/your-repo/issues)
- 📖 Docs: [README.md](../README.md)
