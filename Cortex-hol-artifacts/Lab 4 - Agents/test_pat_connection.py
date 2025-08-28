#!/usr/bin/env python3
"""
Lab 4: Test Programmatic Access Token (PAT) Connection
Test your PAT authentication and verify access to Cortex Agents

Prerequisites:
- Created PAT token through Snowsight UI (see create_pat_token.sql)
- Installed: pip install snowflake-connector-python
"""

import snowflake.connector
import os
import sys
from typing import Optional

def test_pat_connection(
    user: str,
    account: str, 
    pat_token: str,
    warehouse: str = "CORTEX_SEARCH_TUTORIAL_WH",
    database: str = "CORTEX_SEARCH_TUTORIAL_DB",
    schema: str = "PUBLIC"
) -> bool:
    """
    Test PAT authentication and verify access to Cortex resources
    
    Args:
        user: Your Snowflake username
        account: Your Snowflake account identifier
        pat_token: Your Programmatic Access Token secret
        warehouse: Warehouse to use (default: CORTEX_SEARCH_TUTORIAL_WH)
        database: Database to use (default: CORTEX_SEARCH_TUTORIAL_DB)
        schema: Schema to use (default: PUBLIC)
    
    Returns:
        bool: True if connection successful, False otherwise
    """
    try:
        print("🔐 Testing PAT authentication...")
        
        # Create connection using PAT
        ctx = snowflake.connector.connect(
            user=user,
            account=account,
            authenticator='oauth',
            token=pat_token,
            warehouse=warehouse,
            database=database,
            schema=schema
        )
        
        cursor = ctx.cursor()
        
        # Test 1: Basic connection verification
        print("✅ PAT authentication successful!")
        
        cursor.execute("SELECT CURRENT_USER(), CURRENT_ROLE(), CURRENT_WAREHOUSE(), CURRENT_DATABASE()")
        result = cursor.fetchone()
        print(f"   Connected as: {result[0]}")
        print(f"   Current role: {result[1]}")
        print(f"   Using warehouse: {result[2]}")
        print(f"   Using database: {result[3]}")
        
        # Test 2: Verify access to Cortex Search Services
        print("\n🔍 Testing access to Cortex Search Services...")
        try:
            cursor.execute("SHOW CORTEX SEARCH SERVICES IN SCHEMA CORTEX_SEARCH_TUTORIAL_DB.PUBLIC")
            services = cursor.fetchall()
            if services:
                print(f"✅ Found {len(services)} Cortex Search service(s):")
                for service in services:
                    print(f"   - {service[1]}")  # Service name is in column 1
            else:
                print("⚠️  No Cortex Search services found")
        except Exception as e:
            print(f"❌ Error accessing Cortex Search services: {e}")
        
        # Test 3: Verify access to Lab 2 database
        print("\n📊 Testing access to Lab 2 Analyst database...")
        try:
            cursor.execute("SHOW DATABASES LIKE 'CORTEX_ANALYST_DEMO'")
            db_result = cursor.fetchall()
            if db_result:
                print("✅ Lab 2 CORTEX_ANALYST_DEMO database accessible")
            else:
                print("⚠️  Lab 2 CORTEX_ANALYST_DEMO database not found")
        except Exception as e:
            print(f"❌ Error accessing Lab 2 database: {e}")
        
        # Test 4: Verify access to created Cortex Agents
        print("\n🤖 Testing access to Cortex Agents...")
        try:
            cursor.execute("SHOW CORTEX AGENTS")
            agents = cursor.fetchall()
            if agents:
                print(f"✅ Found {len(agents)} Cortex Agent(s):")
                for agent in agents:
                    print(f"   - {agent[1]}")  # Agent name is in column 1
            else:
                print("⚠️  No Cortex Agents found (run setup.sql first)")
        except Exception as e:
            print(f"❌ Error accessing Cortex Agents: {e}")
        
        # Test 5: Test CORTEX_USER role privileges
        print("\n👤 Testing Cortex privileges...")
        try:
            cursor.execute("SELECT CURRENT_AVAILABLE_ROLES()")
            roles_result = cursor.fetchone()
            available_roles = roles_result[0] if roles_result else ""
            
            if "CORTEX_USER" in available_roles:
                print("✅ CORTEX_USER role available")
            else:
                print("⚠️  CORTEX_USER role not available - may need to grant it")
        except Exception as e:
            print(f"❌ Error checking Cortex privileges: {e}")
        
        cursor.close()
        ctx.close()
        
        print("\n🎉 PAT connection test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ PAT connection failed: {e}")
        return False

def main():
    """
    Main function to run PAT connection test
    """
    print("Lab 4 - Cortex Agents PAT Connection Test")
    print("=" * 50)
    
    # Get connection parameters
    user = input("Enter your Snowflake username: ").strip()
    account = input("Enter your Snowflake account identifier: ").strip()
    
    print("\n🔒 Enter your PAT token secret:")
    print("   (This will not be displayed for security)")
    pat_token = input("PAT Token: ").strip()
    
    if not all([user, account, pat_token]):
        print("❌ All fields are required!")
        sys.exit(1)
    
    # Optional: Customize warehouse/database
    use_defaults = input("\nUse default warehouse/database? [Y/n]: ").strip().lower()
    
    if use_defaults in ['n', 'no']:
        warehouse = input("Warehouse [CORTEX_SEARCH_TUTORIAL_WH]: ").strip() or "CORTEX_SEARCH_TUTORIAL_WH"
        database = input("Database [CORTEX_SEARCH_TUTORIAL_DB]: ").strip() or "CORTEX_SEARCH_TUTORIAL_DB"
        schema = input("Schema [PUBLIC]: ").strip() or "PUBLIC"
    else:
        warehouse = "CORTEX_SEARCH_TUTORIAL_WH"
        database = "CORTEX_SEARCH_TUTORIAL_DB"
        schema = "PUBLIC"
    
    print(f"\n🚀 Testing connection to {account} as {user}...")
    
    # Run the test
    success = test_pat_connection(
        user=user,
        account=account,
        pat_token=pat_token,
        warehouse=warehouse,
        database=database,
        schema=schema
    )
    
    if success:
        print("\n✅ Your PAT is configured correctly for Lab 4 Cortex Agents!")
        print("   You can now use this PAT for API connections and demonstrations.")
    else:
        print("\n❌ PAT test failed. Please check:")
        print("   - PAT token is correct and not expired")
        print("   - User has necessary privileges")
        print("   - Services from Labs 1-3 are accessible")

if __name__ == "__main__":
    main()
