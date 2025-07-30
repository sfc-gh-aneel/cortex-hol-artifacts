# Snowflake AI Hands-on Labs

Welcome to the Snowflake AI Hands-on Labs! This repository contains a series of practical exercises designed to help you learn and master Snowflake's AI and ML capabilities, particularly the Cortex family of features.

## 🎯 What You'll Learn

Through these hands-on labs, you'll gain practical experience with:

- **Cortex Search**: Build intelligent search services over your data
- **Cortex Analyst**: Perform natural language analytics and reporting
- **Cortex LLM Functions**: Leverage large language models for text processing
- **Cortex Utility Functions**: Use embedding, sentiment analysis, and more
- **Streamlit Integration**: Create interactive AI-powered applications

## 📋 Prerequisites

Before starting these labs, ensure you have:

- A Snowflake account with necessary privileges to:
  - Create databases, tables, and virtual warehouses
  - Create Cortex Search Services
  - Deploy Streamlit applications
  - Use Cortex AI functions
- Basic familiarity with SQL
- Understanding of Python fundamentals (for Streamlit apps)

### **🧠 Cortex Requirements**

**Important**: Lab 2 (Cortex Analyst) requires additional setup:

1. **Cortex Access**: Your Snowflake account must have Cortex enabled
2. **User Privileges**: You need the `CORTEX_USER` database role:
   ```sql
   GRANT DATABASE ROLE SNOWFLAKE.CORTEX_USER TO USER <your_username>;
   ```
3. **Account Edition**: Cortex Analyst may require specific Snowflake editions
4. **Regional Availability**: Cortex Analyst is not available in all regions yet

**Test Cortex availability** by running:
```sql
SELECT SNOWFLAKE.CORTEX.COMPLETE('snowflake-arctic', 'Hello world');
```

> **New to Snowflake?** Check out [Snowflake in 20 minutes](https://docs.snowflake.com/en/user-guide/getting-started-tutorial) to get started.

## 🧪 Labs Overview

### Lab 1: PDF Chatbot with Cortex Search
**Location**: `Cortex-hol-artifacts/Lab 1 - Search/`

Build an intelligent chatbot that can answer questions about PDF documents using Cortex Search.

**What you'll build**:
- Extract text from PDF documents using `PARSE_DOCUMENT`
- Create a Cortex Search Service for semantic search
- Develop a Streamlit chat application
- Implement retrieval-augmented generation (RAG)

**Key files**:
- `Lab1.sql` - Database setup and search service creation
- `streamlit_app.py` - Interactive chat application
- `docs/` - Sample PDF documents for testing

**Based on**: [Snowflake Tutorial 3: Build a PDF chatbot with Cortex Search](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-search/tutorials/cortex-search-tutorial-3-chat-advanced)

### Lab 2: Cortex Analyst for Business Intelligence *(Coming Soon)*
**Location**: `Cortex-hol-artifacts/Lab 2 - Analyst/`

Learn to use Cortex Analyst for natural language business intelligence and reporting.

### Lab 3: Advanced Text Processing with Cortex Functions *(Coming Soon)*
**Location**: `Cortex-hol-artifacts/Lab 3 - Text Processing/`

Explore Cortex utility functions for embedding, sentiment analysis, and text generation.

## 🚀 Getting Started

1. **Clone this repository**:
   ```bash
   git clone <repository-url>
   cd cortex-hol-artifacts
   ```

2. **Set up your Snowflake environment**:
   - Log into your Snowflake account
   - Ensure you have the necessary privileges listed in prerequisites
   - Note your account identifier and region

3. **Start with Lab 1**:
   ```bash
   cd "Cortex-hol-artifacts/Lab 1 - Search"
   ```

## 📚 Cortex Features Reference

### Cortex Search
Cortex Search enables you to build search experiences using your data stored in Snowflake.

**Key Functions**:
- `CORTEX.SEARCH()` - Query search services
- `CORTEX.PARSE_DOCUMENT()` - Extract text from documents
- `CORTEX.SPLIT_TEXT_RECURSIVE_CHARACTER()` - Chunk text for processing

**Documentation**: [Cortex Search Overview](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-search)

### Cortex LLM Functions
Access large language models directly in SQL for text generation and processing.

**Available Models**:
- `mistral-large2`
- `llama3.1-70b`
- `llama3.1-8b`
- `snowflake-arctic`

**Key Functions**:
- `CORTEX.COMPLETE()` - Text generation and completion
- `CORTEX.TRANSLATE()` - Language translation
- `CORTEX.SUMMARIZE()` - Text summarization

**Documentation**: [Cortex LLM Functions](https://docs.snowflake.com/en/user-guide/snowflake-cortex/llm-functions)

### Cortex Analyst
Natural language interface for business intelligence and analytics.

**Capabilities**:
- Natural language to SQL conversion
- Automated chart and visualization generation
- Business-friendly explanations of data insights

**Documentation**: [Cortex Analyst](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-analyst)

### Cortex Utility Functions
Helper functions for common AI/ML tasks.

**Key Functions**:
- `CORTEX.EMBED_TEXT_768()` / `CORTEX.EMBED_TEXT_1024()` - Text embeddings
- `CORTEX.SENTIMENT()` - Sentiment analysis
- `CORTEX.EXTRACT_ANSWER()` - Question answering

**Documentation**: [Cortex Utility Functions](https://docs.snowflake.com/en/user-guide/snowflake-cortex/ml-functions)

## 🛠️ Common Setup Tasks

### Creating a Cortex-enabled Warehouse
```sql
CREATE OR REPLACE WAREHOUSE cortex_wh WITH
    WAREHOUSE_SIZE='X-SMALL'
    AUTO_SUSPEND = 120
    AUTO_RESUME = TRUE
    INITIALLY_SUSPENDED=TRUE;
```

### Setting up a Database for Labs
```sql
CREATE DATABASE IF NOT EXISTS cortex_labs_db;
USE DATABASE cortex_labs_db;
USE SCHEMA public;
```

### Creating a File Stage
```sql
CREATE OR REPLACE STAGE documents_stage
    DIRECTORY = (ENABLE = TRUE)
    ENCRYPTION = (TYPE = 'SNOWFLAKE_SSE');
```

## 🔗 Additional Resources

### Official Documentation
- [Snowflake Cortex Overview](https://docs.snowflake.com/en/user-guide/snowflake-cortex)
- [Cortex Search Tutorials](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-search/tutorials)
- [Streamlit in Snowflake](https://docs.snowflake.com/en/developer-guide/streamlit/about-streamlit)

### Tutorials and Guides
- [Building AI Applications with Snowflake Cortex](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-search/tutorials/cortex-search-tutorial-1-chat-basic)
- [Working with Document AI](https://docs.snowflake.com/en/user-guide/snowflake-cortex/document-ai)

### Community and Support
- [Snowflake Community](https://community.snowflake.com/)
- [Snowflake Documentation](https://docs.snowflake.com/)
- [Snowflake University](https://university.snowflake.com/)

## 🤝 Contributing

If you find issues or have suggestions for improving these labs:

1. Create an issue describing the problem or enhancement
2. Submit a pull request with your proposed changes
3. Ensure all code follows best practices and includes appropriate documentation

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Need Help?

- Check the individual lab README files for specific guidance
- Review the [Snowflake Documentation](https://docs.snowflake.com/)
- Join the [Snowflake Community](https://community.snowflake.com/) for support

---

**Happy Learning!** 🎉

Start your AI journey with Snowflake Cortex and build powerful, intelligent applications with your data. 