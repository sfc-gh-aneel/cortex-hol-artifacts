/*--
Lab 2: Cortex Analyst for Wealth Management
Based on: https://quickstarts.snowflake.com/guide/getting_started_with_cortex_analyst/
Adapted for Financial Services - Personal Wealth & Retirement Plan Management
--*/

/*--
• Database, schema, warehouse, and stage creation
--*/

USE ROLE SECURITYADMIN;

CREATE ROLE cortex_user_role;
GRANT DATABASE ROLE SNOWFLAKE.CORTEX_USER TO ROLE cortex_user_role;

GRANT ROLE cortex_user_role TO USER <user>;

USE ROLE sysadmin;

-- Create demo database
CREATE OR REPLACE DATABASE cortex_analyst_demo;

-- Create schema
CREATE OR REPLACE SCHEMA cortex_analyst_demo.wealth_management;

-- Create warehouse
CREATE OR REPLACE WAREHOUSE cortex_analyst_wh
    WAREHOUSE_SIZE = 'large'
    WAREHOUSE_TYPE = 'standard'
    AUTO_SUSPEND = 60
    AUTO_RESUME = TRUE
    INITIALLY_SUSPENDED = TRUE
COMMENT = 'Warehouse for Cortex Analyst demo';

GRANT USAGE ON WAREHOUSE cortex_analyst_wh TO ROLE cortex_user_role;
GRANT OPERATE ON WAREHOUSE cortex_analyst_wh TO ROLE cortex_user_role;

GRANT OWNERSHIP ON SCHEMA cortex_analyst_demo.wealth_management TO ROLE cortex_user_role;
GRANT OWNERSHIP ON DATABASE cortex_analyst_demo TO ROLE cortex_user_role;

USE ROLE cortex_user_role;

-- Use the created warehouse
USE WAREHOUSE cortex_analyst_wh;

USE DATABASE cortex_analyst_demo;
USE SCHEMA cortex_analyst_demo.wealth_management;

-- Create stage for raw data
CREATE OR REPLACE STAGE raw_data DIRECTORY = (ENABLE = TRUE);

/*--
• Fact and Dimension Table Creation
--*/

-- Fact table: daily_portfolio_performance
CREATE OR REPLACE TABLE cortex_analyst_demo.wealth_management.daily_portfolio_performance (
    date DATE,
    portfolio_value FLOAT,
    management_fees FLOAT,
    target_portfolio_value FLOAT,
    client_id INT,
    advisor_id INT
);

-- Dimension table: client_dim
CREATE OR REPLACE TABLE cortex_analyst_demo.wealth_management.client_dim (
    client_id INT,
    client_segment VARCHAR(16777216)
);

-- Dimension table: advisor_dim
CREATE OR REPLACE TABLE cortex_analyst_demo.wealth_management.advisor_dim (
    advisor_id INT,
    advisor_region VARCHAR(16777216),
    office_location VARCHAR(16777216),
    advisor_name VARCHAR(16777216),
    advisor_specialty VARCHAR(16777216),
    years_experience INT,
    team_size INT
);

/*--
• Load data into tables
--*/

USE ROLE CORTEX_USER_ROLE;
USE DATABASE CORTEX_ANALYST_DEMO;
USE SCHEMA CORTEX_ANALYST_DEMO.WEALTH_MANAGEMENT;
USE WAREHOUSE CORTEX_ANALYST_WH;

COPY INTO CORTEX_ANALYST_DEMO.WEALTH_MANAGEMENT.DAILY_PORTFOLIO_PERFORMANCE
FROM @raw_data
FILES = ('daily_portfolio_performance.csv')
FILE_FORMAT = (
    TYPE=CSV,
    SKIP_HEADER=1,
    FIELD_DELIMITER=',',
    TRIM_SPACE=FALSE,
    FIELD_OPTIONALLY_ENCLOSED_BY=NONE,
    REPLACE_INVALID_CHARACTERS=TRUE,
    DATE_FORMAT=AUTO,
    TIME_FORMAT=AUTO,
    TIMESTAMP_FORMAT=AUTO
    EMPTY_FIELD_AS_NULL = FALSE
    error_on_column_count_mismatch=false
)
ON_ERROR=CONTINUE
FORCE = TRUE ;

COPY INTO CORTEX_ANALYST_DEMO.WEALTH_MANAGEMENT.CLIENT_DIM
FROM @raw_data
FILES = ('client.csv')
FILE_FORMAT = (
    TYPE=CSV,
    SKIP_HEADER=1,
    FIELD_DELIMITER=',',
    TRIM_SPACE=FALSE,
    FIELD_OPTIONALLY_ENCLOSED_BY=NONE,
    REPLACE_INVALID_CHARACTERS=TRUE,
    DATE_FORMAT=AUTO,
    TIME_FORMAT=AUTO,
    TIMESTAMP_FORMAT=AUTO
    EMPTY_FIELD_AS_NULL = FALSE
    error_on_column_count_mismatch=false
)
ON_ERROR=CONTINUE
FORCE = TRUE ;

COPY INTO CORTEX_ANALYST_DEMO.WEALTH_MANAGEMENT.ADVISOR_DIM
FROM @raw_data
FILES = ('advisor.csv')
FILE_FORMAT = (
    TYPE=CSV,
    SKIP_HEADER=1,
    FIELD_DELIMITER=',',
    TRIM_SPACE=FALSE,
    FIELD_OPTIONALLY_ENCLOSED_BY=NONE,
    REPLACE_INVALID_CHARACTERS=TRUE,
    DATE_FORMAT=AUTO,
    TIME_FORMAT=AUTO,
    TIMESTAMP_FORMAT=AUTO
    EMPTY_FIELD_AS_NULL = FALSE
    error_on_column_count_mismatch=false
)
ON_ERROR=CONTINUE
FORCE = TRUE ;

/*--
• Create Cortex Search Service for enhanced literal string searches
--*/

USE DATABASE cortex_analyst_demo;
USE SCHEMA wealth_management;
USE ROLE cortex_user_role;

CREATE OR REPLACE CORTEX SEARCH SERVICE client_segment_search_service
  ON client_segment
  WAREHOUSE = cortex_analyst_wh
  TARGET_LAG = '1 hour'
  AS (
    SELECT client_segment FROM client_dim
  );

CREATE OR REPLACE CORTEX SEARCH SERVICE advisor_region_search_service
  ON advisor_region
  WAREHOUSE = cortex_analyst_wh
  TARGET_LAG = '1 hour'
  AS (
    SELECT advisor_region FROM advisor_dim
  );

/*--
• Test the data setup
--*/

-- Verify data loaded correctly
SELECT COUNT(*) as portfolio_records FROM daily_portfolio_performance;
SELECT COUNT(*) as client_records FROM client_dim;
SELECT COUNT(*) as advisor_records FROM advisor_dim;

-- Sample data preview
SELECT * FROM daily_portfolio_performance LIMIT 10;
SELECT * FROM client_dim LIMIT 10;
SELECT * FROM advisor_dim LIMIT 10;

/*--
Instructions for completing the lab:

1. Upload the following CSV files to the raw_data stage:
   - daily_portfolio_performance.csv
   - client.csv
   - advisor.csv
   - wealth_management.yaml

2. Run the COPY INTO commands above to load the data

3. Upload the wealth_management.yaml file to the same stage

4. Create a Streamlit in Snowflake app using the streamlit_app.py code

5. Test the conversational interface with questions like:
   - "What questions can I ask?"
   - "What was the total portfolio value last month?"
   - "Which client segment has the highest average portfolio value?"
   - "Show me portfolio performance by advisor region"
--*/ 