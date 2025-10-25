# MCP Servers Configuration

This directory contains configurations for **real external MCP servers**.

## What are MCP Servers?

MCP servers are **external processes** that run separately and provide tools via the Model Context Protocol. They are NOT Python code in this repo.

## Available MCP Servers

### 1. Gmail MCP Server
**File:** `gmail.json`
**Server:** `@gongrzhe/server-gmail-autoauth-mcp`
**Status:** Disabled by default

Enable in `.env`:
```env
GMAIL_MODE=mcp
```

### 2. Calendar MCP Server
**File:** `calendar.json`
**Server:** `@cocal/google-calendar-mcp`
**Status:** Disabled by default

Enable in `.env`:
```env
CALENDAR_MODE=mcp
```

### 3. DateTime MCP Server
**File:** `datetime.json`
**Server:** `mcp-server-time` (Official Anthropic)
**Status:** Disabled by default

Enable in `.env`:
```env
DATETIME_MODE=mcp
```

### 4. Thinking MCP Server
**File:** `thinking.json`
**Server:** `@modelcontextprotocol/server-sequential-thinking` (Official Anthropic)
**Status:** **Enabled by default**

This is always used:
```env
THINKING_MODE=mcp
```

## How MCP Servers Work

### When MODE=tool (Custom Python)
```
User Request → Agent → mcp_tools/gmail_mcp.py → Google API
                       (Direct Python code)
```

### When MODE=mcp (External Server)
```
User Request → Agent → MCP Client → npx @gongrzhe/server-gmail-autoauth-mcp → Google API
                                    (External Node.js process)
```

## Configuration Format

Each JSON file has:
```json
{
  "name": "service_name",
  "description": "What this server does",
  "command": "npx" or "uvx",
  "args": ["package-name"],
  "transport": "stdio",
  "enabled": true/false
}
```

## Installation

MCP servers auto-install when first used:

### NPM-based (npx)
```bash
# Gmail
npx @gongrzhe/server-gmail-autoauth-mcp

# Calendar
npx @cocal/google-calendar-mcp

# Thinking
npx -y @modelcontextprotocol/server-sequential-thinking
```

### Python-based (uvx)
```bash
# DateTime
uvx mcp-server-time
```

## Usage

MCP servers are loaded automatically by `tool_factory.py` when:
1. `*_MODE=mcp` in `.env`
2. `enabled: true` in the JSON config

The factory uses `langchain-mcp-adapters` to connect to these external servers.

## vs mcp_tools/

**mcp_tools/** = Custom Python tools (local code)
**mcp_servers/** = External MCP server configs (remote processes)

Choose via MODE setting in `.env`.
