# Lab 4 - Getting Started with Cortex Agents

Create Cortex Agents for your existing Lab 1-3 services and use them in Snowflake Intelligence for natural language querying.

## Overview

This lab creates three Cortex Agents that connect to the services you built in previous labs:

- **LAB1_DOCUMENT_SEARCH_AGENT**: Natural language search through documents (Lab 1)
- **LAB2_WEALTH_ANALYST_AGENT**: Natural language analytics on wealth management data (Lab 2)  
- **LAB3_MULTIMODAL_SEARCH_AGENT**: Enhanced document analysis with visual content (Lab 3)

## Prerequisites

✅ **Completed Labs 1, 2, and 3** with their Cortex services running  
✅ **CORTEX_USER database role** granted to your user  
✅ **Privileges** to create agents and access the lab databases  

## Quick Start

### 1. Run the Setup

Execute the setup script in Snowflake:

```sql
-- Copy and paste the contents of setup.sql into a Snowflake worksheet
-- Or upload and run the file directly
```

### 2. Access Snowflake Intelligence

1. Navigate to **Snowflake Intelligence** in your Snowflake interface
2. You'll see your three new agents in the agent dropdown
3. Select an agent and start asking questions!

### 3. Try Sample Questions

**LAB1_DOCUMENT_SEARCH_AGENT** (Document Search):
- "Find documents about retirement planning"
- "What information is available about pension distributions?"
- "Search for documents containing 401k information"

**LAB2_WEALTH_ANALYST_AGENT** (Wealth Analytics):
- "What's the total portfolio value by client segment?"
- "Show me the top performing advisors by region"
- "How does portfolio performance compare to targets?"

**LAB3_MULTIMODAL_SEARCH_AGENT** (Enhanced Document Analysis):
- "Analyze the investment trends in the 2023 factbook"
- "What key statistics are shown in the charts?"
- "Extract data from the visual elements in the documents"

## Files

- **`setup.sql`**: Complete setup script that creates all three agents
- **`demo_queries.md`**: Additional sample queries for demonstrations
- **`README.md`**: This file

## Architecture

```
Lab 4 Agents Architecture

┌─────────────────────────────────────────────────────────────┐
│                    Snowflake Intelligence                   │
│                     (Natural Language UI)                  │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
                    Cortex Agents
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
   Lab1 Agent      Lab2 Agent      Lab3 Agent
      │               │               │
      ▼               ▼               ▼
  Cortex Search   Cortex Analyst   Cortex Search
  (Documents)    (Wealth Data)    (Multimodal)
      │               │               │
      ▼               ▼               ▼
  Lab 1 Docs      Lab 2 Data      Lab 3 Docs
```

## Troubleshooting

**Agent not appearing in Snowflake Intelligence?**
- Verify the agent was created: `SHOW CORTEX AGENTS;`
- Check you have the CORTEX_USER role granted
- Ensure you have access to the underlying services

**"Service not found" errors?**
- Verify Labs 1-3 services exist and are accessible
- Check database and schema names in setup.sql match your environment
- Confirm services are in the expected locations

**Permission denied?**
- Ensure CORTEX_USER database role is granted
- Verify access to source databases (CORTEX_SEARCH_TUTORIAL_DB, CORTEX_ANALYST_DEMO)
- Check your role has privileges to create agents

## Demo Tips

1. **Start Simple**: Begin with basic questions to show each agent works
2. **Show Progression**: Demonstrate how the same data can be accessed via natural language vs traditional SQL
3. **Highlight Differences**: Show how each agent specializes in different types of data and queries
4. **Interactive**: Let the audience suggest questions to ask the agents

## Next Steps

- Customize agent instructions for your specific use cases
- Add more sophisticated sample questions
- Integrate agents into applications using the Snowflake APIs
- Monitor agent usage and performance

---

**Based on**: [Snowflake Quickstart - Getting Started with Cortex Agents](https://quickstarts.snowflake.com/guide/getting_started_with_cortex_agents/)
