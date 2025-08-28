-- Lab 4: Create Programmatic Access Token (PAT) for Cortex Agents
-- Based on: https://docs.snowflake.com/en/user-guide/programmatic-access-tokens

/*
This script walks through creating a Programmatic Access Token (PAT) 
for secure authentication with Snowflake APIs and connectors.

IMPORTANT: PATs can only be created through Snowsight UI, not via SQL.
This script provides the SQL commands to verify your setup and permissions.
*/

-- ====================================================================
-- STEP 1: Verify Current User and Context
-- ====================================================================

-- Check current user (this will be the user who gets the PAT)
SELECT CURRENT_USER() AS current_user;

-- Check current role and privileges
SELECT CURRENT_ROLE() AS current_role;
SHOW GRANTS TO USER IDENTIFIER(CURRENT_USER());

-- ====================================================================
-- STEP 2: Verify Required Privileges for PAT Creation
-- ====================================================================

-- Check if user has necessary privileges
-- Note: Users need appropriate role privileges to create PATs
DESCRIBE USER IDENTIFIER(CURRENT_USER());

-- Check available roles for the user
SHOW GRANTS TO USER IDENTIFIER(CURRENT_USER());

-- ====================================================================
-- STEP 3: UI Steps for PAT Creation (Manual Process)
-- ====================================================================

/*
Since PATs must be created through Snowsight UI, follow these steps:

1. LOG INTO SNOWSIGHT:
   - Navigate to your Snowflake account in a web browser
   - Log in with your credentials

2. ACCESS USER PROFILE:
   - Click on your user profile icon (top-right corner)
   - Select "User Profile" from the dropdown menu

3. CREATE NEW PAT:
   - Scroll to "Programmatic Access Tokens" section
   - Click "Create Token" button

4. CONFIGURE TOKEN:
   - Name: "Lab4_Cortex_Agents_Demo"
   - Description: "Token for Lab 4 Cortex Agents demonstrations"
   - Expiration: Set to desired duration (max 365 days)
   - Network Policy: (Optional) Restrict to specific IPs if needed
   - Click "Create"

5. SECURE TOKEN STORAGE:
   - CRITICAL: Copy the token secret immediately
   - Store it securely (password manager, secure notes)
   - This is the ONLY time you'll see the token secret

6. SAVE TOKEN DETAILS:
   - Token Name: Lab4_Cortex_Agents_Demo
   - User: [Your current user from STEP 1]
   - Account: [Your account identifier]
   - Created Date: [Today's date]
*/

-- ====================================================================
-- STEP 4: Test PAT Authentication (After Creation)
-- ====================================================================

-- After creating the PAT, you can test it with Python:
/*
import snowflake.connector

# Replace with your actual values
ctx = snowflake.connector.connect(
    user='YOUR_USERNAME',
    account='YOUR_ACCOUNT_IDENTIFIER', 
    authenticator='oauth',
    token='YOUR_PAT_TOKEN_SECRET',
    warehouse='CORTEX_SEARCH_TUTORIAL_WH',
    database='CORTEX_SEARCH_TUTORIAL_DB',
    schema='PUBLIC'
)

# Test the connection
cursor = ctx.cursor()
cursor.execute("SELECT CURRENT_USER(), CURRENT_ROLE(), CURRENT_WAREHOUSE()")
result = cursor.fetchone()
print(f"Connected as: {result[0]}, Role: {result[1]}, Warehouse: {result[2]}")
cursor.close()
ctx.close()
*/

-- ====================================================================
-- STEP 5: Verify PAT Usage for Cortex Agents
-- ====================================================================

-- Once PAT is created, verify access to required objects
-- (Run these after creating the PAT to ensure it has proper access)

-- Test access to Lab 1 Search Service
SHOW CORTEX SEARCH SERVICES IN SCHEMA CORTEX_SEARCH_TUTORIAL_DB.PUBLIC;

-- Test access to Lab 2 Database/Schema
SHOW DATABASES LIKE 'CORTEX_ANALYST_DEMO';

-- Test access to created agents (after running setup.sql)
SHOW CORTEX AGENTS;

-- ====================================================================
-- STEP 6: PAT Security Best Practices
-- ====================================================================

/*
SECURITY RECOMMENDATIONS:

1. TOKEN ROTATION:
   - Rotate PATs regularly (every 90 days recommended)
   - Use Snowsight to rotate: User Profile > Programmatic Access Tokens > Rotate

2. TOKEN REVOCATION:
   - Immediately revoke compromised tokens
   - Use Snowsight to revoke: User Profile > Programmatic Access Tokens > Delete

3. NETWORK POLICIES:
   - Apply network policies to restrict PAT usage to specific IP ranges
   - Especially important for production environments

4. ROLE-BASED ACCESS:
   - Grant minimal necessary privileges to the user
   - Use specific roles for specific purposes

5. MONITORING:
   - Monitor PAT usage through account usage views
   - Set up alerts for unusual authentication patterns
*/

-- Query to check recent authentications (optional monitoring)
SELECT 
    USER_NAME,
    CLIENT_IP,
    REPORTED_CLIENT_TYPE,
    AUTHENTICATION_METHOD,
    EVENT_TIMESTAMP
FROM SNOWFLAKE.ACCOUNT_USAGE.LOGIN_HISTORY 
WHERE USER_NAME = CURRENT_USER()
AND EVENT_TIMESTAMP >= DATEADD(DAY, -7, CURRENT_TIMESTAMP())
ORDER BY EVENT_TIMESTAMP DESC
LIMIT 10;

SELECT 'PAT creation verification script completed!' AS status,
       'Follow the UI steps above to create your PAT' AS next_action,
       'Test with Python connection code after creation' AS testing;
