# Lab 2: Cortex Analyst for Wealth Management

## Overview

This lab demonstrates how to build a conversational analytics interface using **Snowflake Cortex Analyst** for a financial services company specializing in personal wealth and retirement plan management.

**Based on**: [Snowflake Cortex Analyst Quickstart](https://quickstarts.snowflake.com/guide/getting_started_with_cortex_analyst/index.html?index=..%2F..index#0)

## What You'll Learn

- How to construct and configure a Semantic Model for wealth management data
- How to call the Cortex Analyst REST API using natural language queries
- How to integrate Cortex Search to enhance SQL query generation
- How to build a Streamlit application with conversational analytics interface
- How to enable multi-turn conversations for portfolio analysis

## What You'll Build

- A Semantic Model over sample wealth management data
- A Streamlit in Snowflake (SiS) app with conversational interface to Cortex Analyst
- Interactive dashboards for portfolio performance, client segments, and advisor metrics

## Prerequisites

- A Snowflake account with necessary privileges to:
  - Create databases, tables, and virtual warehouses
  - Create Cortex Search Services  
  - Deploy Streamlit applications
  - Use Cortex AI functions
- Basic familiarity with SQL
- Understanding of Python fundamentals (for Streamlit apps)

## Lab Structure

```
Lab 2 - Analyst/
├── data/                       # Sample data files
│   ├── daily_portfolio_performance.csv  # Sample portfolio data
│   ├── client.csv             # Client dimension data
│   └── advisor.csv            # Advisor dimension data
├── Lab2_setup.sql              # Complete SQL setup script
├── wealth_management.yaml      # Semantic model definition
├── streamlit_app.py            # Interactive chat application
└── README.md                  # This guide
```

## Step-by-Step Instructions

### Step 1: Setup Database and Tables

1. Open **Snowsight** and create a new SQL worksheet
2. Open the `Lab2_setup.sql` file and copy the entire contents
3. **Important**: Replace `<user>` with your actual Snowflake username in this line:
   ```sql
   GRANT ROLE cortex_user_role TO USER <user>;
   ```
4. Run the SQL script section by section:
   - Database, schema, warehouse, and stage creation
   - Fact and dimension table creation
   - **Stop before the COPY INTO commands** - we need to upload data first

### Step 2: Upload Data Files

1. Navigate to **Data** tab in Snowsight
2. Select **Add Data** → **Load files into a stage**
3. Upload these four files from the lab directory:
   - `data/daily_portfolio_performance.csv`
   - `data/client.csv`
   - `data/advisor.csv`
   - `wealth_management.yaml`
4. Select:
   - **Database**: `CORTEX_ANALYST_DEMO`
   - **Schema**: `WEALTH_MANAGEMENT`
   - **Stage**: `RAW_DATA`
5. Click **Upload**

### Step 3: Load Data into Tables

1. Return to your SQL worksheet
2. Run the **Load data into tables** section from `Lab2_setup.sql`
3. Run the **Create Cortex Search Service** section
4. Run the **Test the data setup** section to verify data loaded correctly

### Step 4: Create Streamlit Application

1. Go to **Projects** → **Streamlit** in Snowsight
2. Click **+ Streamlit App**
3. **Important**: Select:
   - **Database**: `cortex_analyst_demo`
   - **Schema**: `wealth_management`
4. In the Streamlit editor:
   - Replace the default code with contents of `streamlit_app.py`
   - The app will automatically use the correct database/schema configuration

### Step 5: Test Your Analytics Assistant

The application provides a conversational interface for analyzing wealth management data. Try these sample questions:

#### Portfolio Performance Questions:
- "What was the total portfolio value last month?"
- "Which month had the highest portfolio performance?"
- "Show me portfolio values by client segment"
- "How much did portfolio values grow in February?"

#### Fee Analysis Questions:
- "What are the total management fees this year?"
- "Which client segment pays the most in fees?"
- "Show me fee trends over time"
- "What's the average daily fee per client?"

#### Performance vs Target Questions:
- "How are we performing against targets?"
- "Which advisor region is exceeding targets?"
- "Show me clients underperforming their benchmarks"
- "What's our target vs actual performance ratio?"

#### Client and Advisor Insights:
- "Which client segment has the highest portfolio value?"
- "How many clients do we have by segment?"
- "Show me portfolio distribution by advisor region"
- "Which advisor manages the most assets?"

### Step 6: Understanding the Semantic Model

The `wealth_management.yaml` file defines how Cortex Analyst understands your data:

#### **Tables Defined:**
- **daily_portfolio_performance**: Daily metrics with portfolio values, fees, and targets
- **client**: Client segments and classifications
- **advisor**: Advisor regions and office locations

#### **Key Measures:**
- `daily_portfolio_value`: Total portfolio worth
- `daily_management_fees`: Fees charged
- `target_portfolio_value`: Performance benchmarks
- `daily_profit`: Net performance after fees
- `performance_vs_target`: Variance from targets

#### **Relationships:**
- Portfolio performance linked to clients and advisors
- Enables cross-dimensional analysis

#### **Verified Queries:**
Pre-defined questions that improve accuracy for similar queries

## Customization Tips

### Adding More Data
- Extend the CSV files with additional months/clients/advisors
- Update the semantic model to include new dimensions or measures
- Add more verified queries for complex business scenarios

### Enhancing the Semantic Model
- Add calculated fields for ROI, fee ratios, or growth rates
- Include more granular time dimensions (weekly, quarterly)
- Add filters for specific client types or performance thresholds

### Streamlit Customization
- Modify the UI to include charts and visualizations
- Add export functionality for reports
- Integrate with other Snowflake features like Alerts

## Troubleshooting

### Common Issues:

1. **"Cannot find semantic model file"**
   - Verify the YAML file was uploaded to the correct stage
   - Check the file path in the Streamlit configuration

2. **"No data returned"**
   - Ensure all CSV files loaded correctly using the test queries
   - Verify table names match the semantic model exactly

3. **"SQL generation errors"**
   - Check that relationships in the YAML file are correct
   - Ensure column names match between tables and semantic model

4. **Permission errors**
   - Verify the `cortex_user_role` was granted to your user
   - Ensure you're using the correct role when running queries

## Next Steps

After completing this lab, consider:

1. **Expanding the dataset** with real financial data
2. **Adding more complex analytics** like risk assessments or portfolio optimization
3. **Integrating with external data sources** using Snowflake's data sharing features
4. **Building production-ready applications** with advanced Streamlit features

## Resources

- [Cortex Analyst Documentation](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-analyst)
- [Semantic Model Reference](https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-analyst/semantic-model-spec)
- [Streamlit in Snowflake Guide](https://docs.snowflake.com/en/developer-guide/streamlit/about-streamlit)
- [Original Quickstart Tutorial](https://quickstarts.snowflake.com/guide/getting_started_with_cortex_analyst/index.html?index=..%2F..index#0) 