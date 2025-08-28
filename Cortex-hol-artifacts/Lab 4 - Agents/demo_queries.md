# Demo Queries for Lab 4 - Cortex Agents

This document provides example queries to test each service integrated with your MCP server.

## 🎯 Quick Test Queries

### Basic Connectivity Test
```
test query
```
*Tests basic MCP server functionality*

## 📊 Cortex Analyst Queries (Structured Data Analysis)

These queries use the wealth management semantic model from Lab 2:

### Performance Analysis
```
How does performance vs target vary by advisor region?
```
*Expected: SQL generation, data analysis, regional performance breakdown*

```
Show me top performing advisors by region
```
*Expected: Ranking analysis with advisor performance metrics*

```
What are the portfolio performance trends over time?
```
*Expected: Time series analysis of portfolio values*

### Client Segmentation
```
Analyze client performance by advisor region and segment
```
*Expected: Multi-dimensional analysis of client data*

```
Which advisor regions have the highest average portfolio values?
```
*Expected: Regional comparison with statistical analysis*

## 🔍 Cortex Search Queries (Document Search)

These queries search through retirement plan documents from Lab 1:

### Retirement Plan Information
```
Find information about retirement plans and 401k requirements
```
*Expected: Document excerpts with citations about 401k plans*

```
When would a plan participant need to execute a salary reduction agreement?
```
*Expected: Specific information about salary reduction timing and requirements*

```
What are the vesting provisions for retirement plans?
```
*Expected: Details about vesting schedules and requirements*

### Plan Administration
```
What are the employer contribution requirements for 401k plans?
```
*Expected: Information about employer matching and contribution rules*

```
How do plan participants make election changes?
```
*Expected: Process information for changing contribution elections*

```
What happens if a plan loses qualified status?
```
*Expected: Information about plan compliance and consequences*

## 🔄 Mixed Queries (Multiple Services)

These queries may trigger both analyst and search capabilities:

### Comprehensive Analysis
```
Analyze advisor performance by region and find relevant retirement plan documentation
```
*Expected: Both SQL analysis and document search results*

```
Show me performance metrics and any related compliance requirements
```
*Expected: Data analysis plus regulatory information*

## 📧 Email Integration Queries

Test the email functionality (requires setup_agents.sql to be executed):

### Simple Email
```
Send an email to adam.neel@snowflake.com with a summary of today's analysis
```
*Expected: Email sent with analysis summary*

### Report Email
```
Email the performance analysis results to the team
```
*Expected: Formatted email with query results*

## 🚀 Advanced Queries

### Complex Analysis
```
Compare performance vs target across all advisor regions, show the variance, and identify outliers. Also find any relevant documentation about performance benchmarks.
```
*Expected: Complex SQL with statistical analysis plus document search*

### Multi-Step Workflow
```
Analyze portfolio performance by region, identify the top performing region, and send an email to adam.neel@snowflake.com with the results
```
*Expected: Analysis → identification → email workflow*

## 🎪 Demo Script

For a complete demonstration, run these queries in sequence:

1. **Start Simple**: `test query` *(verify connectivity)*
2. **Show Analysis**: `How does performance vs target vary by advisor region?` *(demonstrate analyst)*
3. **Show Search**: `Find information about 401k salary reduction agreements` *(demonstrate search)*
4. **Show Integration**: `Email adam.neel@snowflake.com about the latest performance analysis` *(demonstrate email)*
5. **Show Power**: `Analyze top performing advisors and find compliance documentation` *(demonstrate combination)*

## 🔧 Troubleshooting Queries

If you encounter issues, try these diagnostic queries:

### Test Individual Services
```
Search for retirement plan information
```
*Should only trigger search service*

```
Show me advisor regions
```
*Should only trigger analyst service*

### Error Testing
```
Send email to invalid@external.com
```
*Should fail gracefully with proper error message*

## 📝 Response Format Examples

### Successful Analyst Response
```json
{
  "text": "Analysis interpretation...",
  "sql": "SELECT ...",
  "results": {...},
  "citations": []
}
```

### Successful Search Response
```json
{
  "text": "Document information...",
  "citations": [{"source_id": 1, "doc_id": "..."}],
  "sql": "",
  "results": null
}
```

### Error Response
```json
{
  "text": "Error description...",
  "error": "Detailed error message",
  "citations": [],
  "sql": "",
  "results": null
}
```