-- Lab 4: Cortex Agents Setup for Labs 1-3 Services
-- Based on Snowflake Quickstart: Getting Started with Cortex Agents
-- Adapts the quickstart for our existing Lab 1-3 Cortex services

/*
This script creates Cortex Agents that connect to:
- Lab 1: Document Search service 
- Lab 2: Wealth Management Analyst service
- Lab 3: Multimodal Document Search service

Prerequisites:
- Completed Labs 1, 2, and 3 with their Cortex services
- CORTEX_USER database role granted to your user
- Required privileges on databases and schemas
*/

-- Set context
USE ROLE SYSADMIN;
USE WAREHOUSE CORTEX_SEARCH_TUTORIAL_WH;

-- ====================================================================
-- STEP 1: Verify Prerequisites - Check Existing Services from Labs 1-3
-- ====================================================================

-- Check Lab 1 Search Service
SHOW CORTEX SEARCH SERVICES IN SCHEMA CORTEX_SEARCH_TUTORIAL_DB.PUBLIC;

-- Check Lab 2 Database/Schema (Analyst uses semantic model, not a service)
SHOW DATABASES LIKE 'CORTEX_ANALYST_DEMO';
SHOW SCHEMAS IN DATABASE CORTEX_ANALYST_DEMO;

-- Check Lab 3 Search Service (should be in same location as Lab 1)
-- This will show both Lab 1 and Lab 3 services
SELECT * FROM TABLE(RESULT_SCAN(LAST_QUERY_ID(-2)));

-- ====================================================================
-- STEP 2: Grant Required Cortex Privileges
-- ====================================================================

-- Grant CORTEX_USER database role (required for all Cortex features)
GRANT DATABASE ROLE SNOWFLAKE.CORTEX_USER TO ROLE SYSADMIN;

-- Grant usage on the schemas containing our services
GRANT USAGE ON DATABASE CORTEX_SEARCH_TUTORIAL_DB TO ROLE SYSADMIN;
GRANT USAGE ON SCHEMA CORTEX_SEARCH_TUTORIAL_DB.PUBLIC TO ROLE SYSADMIN;
GRANT USAGE ON DATABASE CORTEX_ANALYST_DEMO TO ROLE SYSADMIN;
GRANT USAGE ON SCHEMA CORTEX_ANALYST_DEMO.WEALTH_MANAGEMENT TO ROLE SYSADMIN;

-- ====================================================================
-- STEP 3: Create Cortex Agents for Each Lab Service
-- ====================================================================

-- LAB 1 SEARCH AGENT: Document Search
-- Connects to the document search service from Lab 1
CREATE OR REPLACE CORTEX AGENT LAB1_DOCUMENT_SEARCH_AGENT
    COMMENT = 'Agent for searching through retirement and pension documents from Lab 1'
    INSTRUCTIONS = 'You are a specialized retirement planning assistant focused on searching through pension and 401k documentation. Your primary objectives are: For document searches, utilize the Cortex Search service to find relevant information about retirement plans, pension considerations, QACA provisions, trust agreements, and wrap documents. Extract specific requirements, regulations, and guidelines from the documents. Summarize findings in clear, focused responses while maintaining context from the original documents. Operating guidelines: Always identify that you are using Cortex Search for document retrieval. Present regulatory information accurately with proper citations. Keep responses focused on the specific query while providing essential context. Do not speculate beyond available documentation.'
    TOOLS = (CORTEX_SEARCH_TUTORIAL_DB.PUBLIC.DOCUMENT_SEARCH_SERVICE);

-- LAB 2 ANALYST AGENT: Wealth Management Analytics  
-- Connects to the wealth management semantic model from Lab 2
CREATE OR REPLACE CORTEX AGENT LAB2_WEALTH_ANALYST_AGENT
    COMMENT = 'Agent for wealth management analytics and portfolio insights from Lab 2 data'
    INSTRUCTIONS = 'You are a specialized wealth management analytics assistant focused on providing concise responses about portfolio metrics, client performance, and advisor analytics. Your primary objectives are: For structured data queries (portfolio values, performance metrics, client segments, advisor KPIs), use the Cortex Analyst YAML-based functionality to generate SQL queries against the wealth management data. Provide direct, numerical answers with minimal explanation. Format responses clearly with relevant units, percentages, and time periods. Present client segmentation data, portfolio performance vs targets, and advisor metrics in structured format. Operating guidelines: Always identify that you are using Cortex Analyst for structured data analysis. Keep responses under 3-4 sentences when possible. Present financial data with appropriate precision and context. Do not speculate beyond available portfolio data.'
    TOOLS = (CORTEX_ANALYST_DEMO.WEALTH_MANAGEMENT.RAW_DATA);

-- LAB 3 MULTIMODAL SEARCH AGENT: Enhanced Document Analysis
-- Connects to the enhanced search service from Lab 3
CREATE OR REPLACE CORTEX AGENT LAB3_MULTIMODAL_SEARCH_AGENT  
    COMMENT = 'Agent for multimodal document analysis including text and image content from Lab 3'
    INSTRUCTIONS = 'You are a specialized investment intelligence assistant focused on analyzing complex financial documents including charts, tables, and visual data from the 2023 ICI Investment Company Fact Book. Your primary objectives are: For multimodal content analysis, utilize the enhanced Cortex Search service to extract insights from both text and visual elements including statistical tables, pie charts, bar graphs, and infographics. Extract precise numerical data, asset allocation percentages, fund performance metrics, and investment trends. Analyze visual data representations and provide accurate interpretations of charts and tables. Operating guidelines: Always identify that you are using enhanced Cortex Search for multimodal analysis. Present numerical data with exact figures and appropriate precision. Distinguish between different data visualization types (tables vs charts vs graphs). Keep responses focused on factual data extraction without speculation beyond documented content.'
    TOOLS = (CORTEX_SEARCH_TUTORIAL_DB.PUBLIC.DOCS_SEARCH_SERVICE);

-- ====================================================================
-- STEP 4: Verify Agent Creation
-- ====================================================================

-- List all created agents
SHOW CORTEX AGENTS;

-- Check specific agent details
DESCRIBE CORTEX AGENT LAB1_DOCUMENT_SEARCH_AGENT;
DESCRIBE CORTEX AGENT LAB2_WEALTH_ANALYST_AGENT;
DESCRIBE CORTEX AGENT LAB3_MULTIMODAL_SEARCH_AGENT;

-- ====================================================================
-- STEP 5: Test Agents (Optional - for verification)
-- ====================================================================

-- These are sample queries you can test in Snowflake Intelligence UI
-- or programmatically once the agents are created

/*
Sample questions for LAB1_DOCUMENT_SEARCH_AGENT:
- "Find documents about retirement planning"
- "What information is available about pension distributions?"
- "Search for documents containing 401k information"

Sample questions for LAB2_WEALTH_ANALYST_AGENT:
- "What's the total portfolio value by client segment?"
- "Show me the top performing advisors by region"
- "How does portfolio performance compare to targets?"

Sample questions for LAB3_MULTIMODAL_SEARCH_AGENT:
- "Analyze the investment trends in the 2023 factbook"
- "What key statistics are shown in the charts?"
- "Extract data from the visual elements in the documents"
*/

SELECT 'Lab 4 - Cortex Agents setup completed successfully!' AS status,
       'Agents are now available in Snowflake Intelligence' AS next_steps;
