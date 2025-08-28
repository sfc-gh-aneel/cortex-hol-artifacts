# Lab 4 - Cortex Agents & MCP Server

This lab demonstrates how to integrate Snowflake Cortex services from Labs 1-3 with external applications using the Model Context Protocol (MCP). We build upon the existing services to create a comprehensive agent experience.

## Overview

This lab follows two key Snowflake quickstarts but adapts them to use the services created in our previous labs:

1. **[Getting Started with Snowflake Intelligence](https://quickstarts.snowflake.com/guide/getting-started-with-snowflake-intelligence/index.html)** - Setting up Cortex Agents in Snowflake
2. **[MCP Server for Cortex Agents](https://quickstarts.snowflake.com/guide/mcp-server-for-cortex-agents/index.html)** - Exposing agents via Model Context Protocol

## Prerequisites

✅ **Completed Previous Labs:**
- **Lab 1**: Document Search service created
- **Lab 2**: Wealth Management Analyst service created  
- **Lab 3**: Multimodal Document Search service created

✅ **Required Roles & Permissions:**
- `ACCOUNTADMIN` role for PAT creation and permissions
- `CORTEX_USER` role granted to your user
- Access to the databases and schemas from Labs 1-3

✅ **Local Development Setup:**
- Python 3.10+ installed
- Git installed
- Claude Desktop installed

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────────┐
│   Claude Desktop │────│   MCP Server     │────│  Snowflake Cortex   │
│                 │    │  (Local Python)  │    │                     │
│   - Chat UI     │    │  - Authentication│    │  - Search Services  │
│   - Tool calls  │    │  - API calls     │    │  - Analyst Services │
│                 │    │  - Response      │    │  - Email Tools      │
│                 │    │    formatting    │    │                     │
└─────────────────┘    └──────────────────┘    └─────────────────────┘
```

## Services Integration

Our MCP server connects to these existing services:

| Service | Source Lab | Purpose |
|---------|------------|---------|
| `CORTEX_ANALYST_DEMO.WEALTH_MANAGEMENT.DOCUMENT_SEARCH_SERVICE` | Lab 1 | Document search & retrieval |
| Wealth Management Semantic Model | Lab 2 | Structured data analysis |
| Multimodal Document Service | Lab 3 | Advanced document parsing |

## Setup Instructions

### Step 1: Snowflake Setup

1. **Create PAT Token:**
   ```sql
   -- Run the PAT creation script
   -- See: create_pat_token.sql for detailed instructions
   ```

2. **Set up Snowflake Intelligence:**
   ```sql
   -- Run the agents setup script
   -- This creates email functionality and required schemas
   -- See: setup_agents.sql
   ```

### Step 2: Local MCP Server Setup

1. **Clone the MCP repository:**
   ```bash
   git clone https://github.com/Snowflake-Labs/sfguide-mcp-cortex-agent.git
   cd sfguide-mcp-cortex-agent
   ```

2. **Install dependencies:**
   ```bash
   # Install uv (fast Python package manager)
   curl -LsSf https://astral.sh/uv/install.sh | sh
   export PATH="$HOME/.local/bin:$PATH"
   
   # Create virtual environment and install packages
   uv venv
   source .venv/bin/activate  # macOS/Linux
   uv add "mcp[cli]" httpx
   ```

3. **Configure environment:**
   ```bash
   # Create .env file
   cat > .env << EOF
   SNOWFLAKE_ACCOUNT_URL=https://your-account.snowflakecomputing.com
   SNOWFLAKE_PAT=your_pat_token_here
   SEMANTIC_MODEL_FILE=@CORTEX_ANALYST_DEMO.WEALTH_MANAGEMENT.RAW_DATA/wealth_management.yaml
   CORTEX_SEARCH_SERVICE=CORTEX_ANALYST_DEMO.WEALTH_MANAGEMENT.DOCUMENT_SEARCH_SERVICE
   EOF
   ```

### Step 3: Claude Desktop Integration

1. **Configure Claude Desktop:**
   ```json
   {
     "mcpServers": {
       "cortex-agent": {
         "command": "/Users/your-username/.local/bin/uv",
         "args": [
           "run",
           "--directory",
           "/Users/your-username/sfguide-mcp-cortex-agent",
           "cortex_agents.py"
         ],
         "env": {
           "PATH": "/Users/your-username/.local/bin:/usr/local/bin:/usr/bin:/bin"
         }
       }
     }
   }
   ```

2. **Restart Claude Desktop** and test the connection.

## Testing & Usage

### Available Capabilities

**📊 Structured Data Analysis (Cortex Analyst):**
- `"How does performance vs target vary by advisor region?"`
- `"Show me top performing advisors by client segment"`
- `"What are the trends in portfolio performance over time?"`

**🔍 Document Search (Cortex Search):**
- `"Find information about retirement plans and 401k requirements"`
- `"When would a plan participant need to execute a salary reduction agreement?"`
- `"What are the vesting provisions for our retirement plans?"`

**📧 Email Notifications:**
- `"Send an email to adam.neel@snowflake.com about the latest analysis"`
- `"Email the performance report to the team"`

### Example Queries

```
User: "How does performance vs target vary by advisor region?"
Response: 
- Generates SQL query analyzing performance metrics
- Returns data showing regional performance variations
- Provides clear interpretation of results

User: "Find information about 401k salary reduction agreements"
Response:
- Searches through retirement plan documents
- Returns relevant excerpts with citations
- Provides comprehensive answer about requirements
```

## Troubleshooting

### Common Issues

**1. 401 Unauthorized Error:**
- Check if PAT token is valid and not expired
- Verify ACCOUNTADMIN role access
- Ensure `.env` file is properly loaded

**2. Tool execution failed:**
- Restart Claude Desktop completely (⌘+Q and reopen)
- Check Claude Desktop logs for specific errors
- Verify MCP server configuration paths

**3. Permission errors:**
- Ensure all required permissions are granted (see setup_agents.sql)
- Verify access to stages and tables from Labs 1-3
- Check that CORTEX_USER role is granted

### Log Monitoring

Monitor Claude Desktop logs for debugging:
```bash
tail -f ~/Library/Logs/Claude/mcp-server-cortex-agent.log
```

## File Reference

| File | Purpose |
|------|---------|
| `setup_agents.sql` | Complete Snowflake setup including email functionality |
| `create_pat_token.sql` | Step-by-step PAT creation guide |
| `test_pat_connection.py` | Test script for validating PAT connectivity |
| `mcp_setup_guide.md` | Detailed local environment setup instructions |
| `demo_queries.md` | Example queries for testing each service |

## Security Considerations

- **PAT Tokens**: Store securely, rotate regularly
- **Email Recipients**: Only pre-approved addresses can receive emails
- **Service Access**: Principle of least privilege for database access
- **Environment Variables**: Never commit `.env` files to version control

## Next Steps

After completing this lab, you can:

1. **Extend Services**: Add more Cortex services to the MCP server
2. **Custom Tools**: Implement additional tools beyond search and analysis
3. **Enterprise Integration**: Deploy MCP server for team/organization use
4. **Advanced Queries**: Explore complex multi-service queries

## Support

- **Snowflake Documentation**: [Cortex Agents](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents)
- **MCP Documentation**: [Model Context Protocol](https://modelcontextprotocol.io/)
- **Quickstart Guides**: See links in overview section above