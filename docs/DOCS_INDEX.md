# Documentation Index

Complete documentation for the WhatsApp HR Assistant project.

## 🚀 Getting Started

### Quick Start
1. [README.md](../README.md) - Project overview and quick start
2. [Setup Guides](./setup/) - Installation and configuration guides
   - [Checkpointer Setup](./setup/CHECKPOINTER_SETUP.md) - PostgreSQL memory setup

## 🔧 Configuration

### Tool Configuration (NEW ⭐)
- **[Dynamic Tool Configuration Guide](./DYNAMIC_TOOL_CONFIG.md)** - Complete guide for YAML-based per-tool configuration
- **[Dynamic Tool Summary](./DYNAMIC_TOOL_SUMMARY.md)** - Quick reference card
- **[Tool Configuration Migration](./TOOL_CONFIG_MIGRATION.md)** - Migrate from old to new system

### Legacy Tool Modes (Deprecated)
- [Tool Modes Comparison](./TOOL_MODES_COMPARISON.md) - Old system comparison
- [Tool Modes Guide](./TOOL_MODES_GUIDE.md) - Old system guide

## 🔌 MCP Integration

### Core Documentation
- **[MCP Integration Overview](../src/mcp_integration/README.md)** - Complete MCP system overview
- **[MCP Client Guide](../src/mcp_integration/client/README.md)** - External MCP client documentation
- [MCP Transport Types](../src/mcp_integration/client/mcp_transports_readme.md) - All transport types explained
- [MCP Quick Reference](../src/mcp_integration/client/quick_reference.md) - Cheat sheet
- [MCP Deployment Guide](../src/mcp_integration/client/deployment_guide.md) - Production deployment

### Legacy MCP Docs (Archived)
- [MCP Integration Guide](./MCP_INTEGRATION_GUIDE.md) - Old integration guide (see new docs above)

## 🛠️ Development Guides

### Adding Features
- [How to Add Tools](./HOW_TO_ADD_TOOLS.md) - Guide for adding new tools
- [Tool System Guide](./guides/TOOL_SYSTEM_GUIDE.md) - Tool architecture overview

### OAuth & Google APIs
- [OAuth Migration Guide](./OAUTH_MIGRATION_GUIDE.md) - OAuth 2.0 setup
- [Fix Google APIs](./fix_google_apis.md) - Google API troubleshooting
- [Fix Permissions](./FIX_PERMISSIONS.md) - Permission issues

## 🐛 Troubleshooting

- [General Troubleshooting](./TROUBLESHOOTING.md) - Common issues and solutions
- [Memory Troubleshooting](./guides/MEMORY_TROUBLESHOOTING.md) - PostgreSQL checkpointer issues

## 📚 Reference

### Architecture
- [Project Guide](../PROJECT_GUIDE.md) - Complete project architecture

### Testing
- [Notebooks](../tests/notebooks/) - Jupyter notebooks for testing
  - `01_tools_testing.ipynb` - Individual tool tests
  - `02_agents_testing.ipynb` - Agent functionality tests
  - `03_custom_agent_tutorial.ipynb` - Build custom agents
  - `04_mcp_integration.ipynb` - Complete MCP system tests
  - `comprehensive_test.ipynb` - End-to-end system tests

## 📦 Archive

Historical documentation (kept for reference):
- [Archive Directory](./archive/) - Old migration guides and transformation docs

---

## 📖 Quick Navigation

**For New Users:**
1. Start with [README.md](../README.md)
2. Follow [Checkpointer Setup](./setup/CHECKPOINTER_SETUP.md)
3. Read [Dynamic Tool Config Guide](./DYNAMIC_TOOL_CONFIG.md)

**For Tool Configuration:**
1. **Use [Dynamic Tool Config](./DYNAMIC_TOOL_CONFIG.md)** (recommended)
2. Edit `src/config/tool_config.yaml`
3. Set `TOOL_MODE=dynamic` in `.env`

**For MCP Development:**
1. Read [MCP Integration Overview](../src/mcp_integration/README.md)
2. Check [MCP Client Guide](../src/mcp_integration/client/README.md)
3. Review [Transport Types](../src/mcp_integration/client/mcp_transports_readme.md)

**For Troubleshooting:**
1. Check [Troubleshooting Guide](./TROUBLESHOOTING.md)
2. Review [Memory Troubleshooting](./guides/MEMORY_TROUBLESHOOTING.md)
3. Search [Archive](./archive/) for historical issues

---

**Last Updated:** October 2025
