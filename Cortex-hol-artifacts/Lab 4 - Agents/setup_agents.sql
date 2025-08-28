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
CREATE DATABASE IF NOT EXISTS SNOWFLAKE_INTELLIGENCE;
CREATE SCHEMA IF NOT EXISTS SNOWFLAKE_INTELLIGENCE.AGENTS;
USE WAREHOUSE CORTEX_SEARCH_TUTORIAL_WH;

/*
===============================================================================
EMAIL SENDER FOR SNOWFLAKE INTELLIGENCE
===============================================================================

This SQL script creates a complete Snowflake stored procedure that sends emails
directly from Snowflake Intelligence. The procedure uses Snowflake's native
notification integration to send emails to pre-approved recipients.

WORKFLOW OVERVIEW:
1. Configure allowed email recipients in notification integration
2. Deploy the SEND_EMAIL stored procedure
3. Call procedure with recipient, subject, and body to send emails immediately
4. Receive instant success/failure feedback

FEATURES:
- Direct email sending with immediate response
- Pre-approved recipient validation for security
- Plain text email support
- Instant success/failure feedback
- Returns detailed JSON responses

PREREQUISITES:
- Snowflake ACCOUNTADMIN role for notification integration setup
- Pre-approved list of email recipients
- SYSADMIN role for procedure deployment

TABLE OF CONTENTS (Search for these markers):
- [SECTION_1_SCHEMAS]     : Database and schema creation
- [SECTION_2_INTEGRATION] : Email notification integration setup
- [SECTION_3_PROCEDURE]   : Main stored procedure definition
- [SECTION_4_EXAMPLES]    : Grant usage permissions and examples

===============================================================================
*/

-- [SECTION_1_SCHEMAS] Database and Schema Creation
-- ================================================
CREATE DATABASE IF NOT EXISTS SNOWFLAKE_INTELLIGENCE;
CREATE SCHEMA IF NOT EXISTS SNOWFLAKE_INTELLIGENCE.TOOLS;

-- [SECTION_2_INTEGRATION] Email Notification Integration Setup
-- ============================================================
USE ROLE ACCOUNTADMIN;

CREATE OR REPLACE NOTIFICATION INTEGRATION SNOWFLAKE_INTELLIGENCE_EMAIL
TYPE = EMAIL
ENABLED = TRUE
ALLOWED_RECIPIENTS = (
    -- IMPORTANT: Replace these with your actual allowed email recipients
    -- Add all email addresses that should be able to receive emails from this tool
    'adam.neel@snowflake.com'
);

GRANT USAGE ON INTEGRATION SNOWFLAKE_INTELLIGENCE_EMAIL TO ROLE SYSADMIN;

-- Verify the integration was created successfully
SHOW INTEGRATIONS LIKE 'SNOWFLAKE_INTELLIGENCE_EMAIL';

-- [SECTION_3_PROCEDURE] Main Stored Procedure Definition
-- ======================================================
USE ROLE SYSADMIN;
USE SCHEMA SNOWFLAKE_INTELLIGENCE.TOOLS;

-- Create the email sending stored procedure
CREATE OR REPLACE PROCEDURE SEND_EMAIL(
    recipient_email STRING,
    subject STRING,
    body STRING
)
RETURNS STRING
LANGUAGE SQL
EXECUTE AS OWNER
AS $$
BEGIN
    -- Send email directly using Snowflake's notification system
    CALL SYSTEM$SEND_EMAIL(
        'SNOWFLAKE_INTELLIGENCE_EMAIL',
        :recipient_email,
        :subject,
        :body,
        'text/html'
    );
    
    -- Return success message
    RETURN OBJECT_CONSTRUCT(
        'status', 'success',
        'message', 'Email sent successfully',
        'recipient', :recipient_email,
        'subject', :subject,
        'timestamp', CURRENT_TIMESTAMP()::STRING
    )::STRING;
    
EXCEPTION
    WHEN OTHER THEN
        RETURN OBJECT_CONSTRUCT(
            'status', 'error',
            'error', 'Failed to send email',
            'details', SQLERRM,
            'recipient', :recipient_email,
            'subject', :subject,
            'timestamp', CURRENT_TIMESTAMP()::STRING
        )::STRING;
END;
$$;

-- [SECTION_4_MANAGEMENT] Managing Allowed Recipients
-- ==================================================

-- Query to view current allowed recipients
DESCRIBE INTEGRATION SNOWFLAKE_INTELLIGENCE_EMAIL;

-- Query to add more recipients to the allowed list
-- IMPORTANT: You must include ALL existing recipients plus new ones
-- Example: Adding a new recipient while keeping existing ones
ALTER NOTIFICATION INTEGRATION SNOWFLAKE_INTELLIGENCE_EMAIL 
SET ALLOWED_RECIPIENTS = (
    'adam.neel@snowflake.com'
);

-- Template for expanding the list (uncomment and modify as needed)
/*
ALTER NOTIFICATION INTEGRATION SNOWFLAKE_INTELLIGENCE_EMAIL 
SET ALLOWED_RECIPIENTS = (
    'tony.gordonjr@snowflake.com'
);
*/

-- [SECTION_5_EXAMPLES] Usage Examples and Test Calls
-- ====================================================

-- Grant necessary permissions
GRANT USAGE ON INTEGRATION SNOWFLAKE_INTELLIGENCE_EMAIL TO ROLE SYSADMIN;

-- Example 1: Simple test email
CALL SNOWFLAKE_INTELLIGENCE.TOOLS.SEND_EMAIL(
    'adam.neel@snowflake.com',
    'Test Email from Snowflake Intelligence',
    'This is a test email to verify the email tool is working correctly.

    If you receive this email, the SEND_EMAIL procedure is functioning properly.

    Best regards,
    Snowflake Intelligence Email Tool'
);

-- Example 2: Report notification email
CALL SNOWFLAKE_INTELLIGENCE.TOOLS.SEND_EMAIL(
    'adam.neel@snowflake.com',
    'Weekly Report Available',
    'Hello Team,

    The weekly sales report has been generated and is ready for review.

    Key Highlights:
    - Total Sales: $125,000 (+8% vs last week)
    - New Customers: 45
    - Top Region: North America

    You can access the full report in the REPORTS.WEEKLY.SALES table.

    Best regards,
    Snowflake Intelligence'
);

-- Example 3: Alert notification
CALL SNOWFLAKE_INTELLIGENCE.TOOLS.SEND_EMAIL(
    'adam.neel@snowflake.com',
    'ALERT: Data Quality Issue Detected',
    'Admin Team,

    A data quality issue has been detected in the daily ETL process.

    Issue Details:
    - Table: SALES.DAILY_TRANSACTIONS
    - Problem: 150 records with NULL customer_id
    - Impact: Moderate
    - Time Detected: 2024-01-21 09:30 AM

    Please investigate and resolve at your earliest convenience.

    Snowflake Intelligence Monitoring'
);

/*
===============================================================================
USAGE INSTRUCTIONS FOR SNOWFLAKE INTELLIGENCE
===============================================================================

When users make requests like:
- "Send an email to adam.neel@snowflake.com about the report"
- "Email the analysis results to adam.neel@snowflake.com"  
- "Alert adam.neel@snowflake.com about the issue"

Snowflake Intelligence should:

1. Extract the email components:
   - recipient_email: Parse from user request
   - subject: Generate appropriate subject or use user-provided one
   - body: Format the content appropriately

2. Call the procedure:
   CALL SNOWFLAKE_INTELLIGENCE.TOOLS.SEND_EMAIL(recipient, subject, body)

3. Check the response:
   - If status = "success": Inform user "Email sent to [recipient]"
   - If status = "error": Inform user "Unable to send email: [error details]"

IMPORTANT SECURITY NOTES:
- Only emails in ALLOWED_RECIPIENTS can receive emails
- Cannot send to arbitrary external email addresses
- Email content is plain text only (no HTML or attachments)
- All email attempts are logged in Snowflake's system logs

===============================================================================
*/
