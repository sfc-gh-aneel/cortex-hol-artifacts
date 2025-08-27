# Lab 4 - Cortex Agents

Create Snowflake Cortex Agents for existing services from Labs 1-3 and set up automated email summaries for Snowflake Intelligence.

## 📚 What You'll Create

- **LAB1_SEARCH_AGENT**: Agent for Lab 1's document search service
- **LAB2_ANALYST_AGENT**: Agent for Lab 2's wealth management analytics  
- **LAB3_SEARCH_AGENT**: Agent for Lab 3's multimodal document parsing
- **Email Infrastructure**: Automated daily summaries of Snowflake Intelligence activity

## 🚀 Quick Start

1. **Open the notebook** `Lab4_Agents_Setup.ipynb` in Snowflake
2. **Update configuration** in the first code cell with your service names
3. **Run all cells sequentially** - the notebook guides you through everything
4. **Test your agents** in Snowflake Intelligence

## 📋 Prerequisites

- ✅ Completed Labs 1, 2, and 3 with their Cortex services
- ✅ Snowflake role with privileges to create agents, procedures, and tasks
- ✅ (Optional) Email notification integration for automated summaries

## 📖 Notebook Contents

### Configuration & Setup
- Easy-to-edit service names and database references
- Environment setup and validation
- Prerequisites checking

### Agent Creation
- Creates agents for all three lab services
- Automatic binding to existing Cortex Search and Analyst services
- Built-in verification and testing

### Email Infrastructure
- `SEND_ANALYSIS_EMAIL` stored procedure
- `EMAIL_ANALYSIS_TASK` scheduled task for daily reports
- Customizable email content and scheduling

### Comprehensive Testing
- Prerequisites validation
- Agent functionality verification
- Health check summary
- Troubleshooting guidance

## 🎯 Using Your Agents

Once created, your agents are immediately available in **Snowflake Intelligence**:

### Sample Queries by Agent:

**LAB1_SEARCH_AGENT** (Document Search):
- "Find documents about pension considerations"
- "Search for retirement planning guidelines"
- "What documents mention 401k distributions?"

**LAB2_ANALYST_AGENT** (Wealth Management):
- "What's the total portfolio value by client segment?"
- "Show me performance vs target by advisor region"
- "Which advisors have the highest average portfolio performance?"

**LAB3_SEARCH_AGENT** (Multimodal Document Parsing):
- "Analyze the 2023 factbook for investment trends"
- "What are the key statistics in the factbook?"
- "Find charts showing asset allocation data"

## 📧 Email Summaries

Configure automated daily summaries:

1. **Set up notification integration** in Snowflake
2. **Update email settings** in the notebook configuration
3. **Enable the task** when ready for automated emails
4. **Customize content** by modifying the stored procedure

## 🔧 Troubleshooting

### Common Issues:

**"Service not found"**
- Verify Labs 1-3 services exist and are accessible
- Check service names in configuration section

**"Permission denied"**
- Ensure your role can create agents, procedures, and tasks
- Check database/schema access permissions

**"Agent not appearing in Snowflake Intelligence"**
- Run the verification cells in the notebook
- Confirm agents were created successfully

**"Email not working"**
- Verify notification integration is configured
- Test the email procedure manually first

## 🏗️ Architecture

```
Lab 4 Agents
├── LAB1_SEARCH_AGENT ──→ Lab 1 Cortex Search Service
├── LAB2_ANALYST_AGENT ──→ Lab 2 Cortex Analyst Service  
├── LAB3_SEARCH_AGENT ──→ Lab 3 Cortex Search Service
└── Email Infrastructure
    ├── SEND_ANALYSIS_EMAIL (procedure)
    └── EMAIL_ANALYSIS_TASK (scheduled task)
```

## 📝 File Structure

```
Lab 4 - Agents/
├── Lab4_Agents_Setup.ipynb    # Complete setup and documentation
└── README.md                  # This file
```

## 🎉 Next Steps

1. **Test your setup** using the notebook's testing cells
2. **Try your agents** in Snowflake Intelligence
3. **Customize email summaries** for your team's needs
4. **Monitor usage** through task execution history

Your agents are now ready to provide natural language access to all your Cortex services through Snowflake Intelligence!

---

**Need help?** The notebook includes comprehensive testing and troubleshooting sections to guide you through any issues.
