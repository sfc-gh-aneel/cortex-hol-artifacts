#!/usr/bin/env python3
"""
Simple MCP Client - Makes direct HTTP calls to Snowflake MCP server
Based on: https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents-mcp#initialize-the-mcp-server

Usage:
    python simple_mcp_client.py init
    python simple_mcp_client.py list
    python simple_mcp_client.py search "retirement plan documents"
    python simple_mcp_client.py analyst "What's the total portfolio value?"
"""

import requests
import json
import sys
import os
from urllib.parse import quote

def load_secrets():
    """Load secrets from secrets.json file"""
    secrets_file = "secrets.json"
    
    if not os.path.exists(secrets_file):
        print("secrets.json not found!")
        print("Create it from the template:")
        print("   1. Copy secrets.json.template to secrets.json")
        print("   2. Update with your Snowflake credentials")
        print("   3. Run the script again")
        print()
        print("Example:")
        print("   cp secrets.json.template secrets.json")
        print("   # Edit secrets.json with your info")
        sys.exit(1)
    
    try:
        with open(secrets_file, 'r') as f:
            secrets = json.load(f)
        
        # Validate required fields
        required = ['account', 'database', 'schema', 'mcp_server_name', 'username', 'password']
        missing = [field for field in required if not secrets.get(field)]
        
        if missing:
            print(f"Missing required fields in secrets.json: {', '.join(missing)}")
            sys.exit(1)
            
        return secrets
        
    except json.JSONDecodeError as e:
        print(f"Invalid JSON in secrets.json: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading secrets.json: {e}")
        sys.exit(1)

# Load configuration from secrets file
secrets = load_secrets()
ACCOUNT = secrets['account']
DATABASE = secrets['database']
SCHEMA = secrets['schema'] 
MCP_SERVER_NAME = secrets['mcp_server_name']
USERNAME = secrets['username']
PASSWORD = secrets['password']

print(f"Loaded config: {USERNAME}@{ACCOUNT} -> {DATABASE}.{SCHEMA}.{MCP_SERVER_NAME}")
print()

# Snowflake REST API base URL
BASE_URL = f"https://{ACCOUNT}.snowflakecomputing.com"

def get_auth_token():
    """Get Snowflake auth token"""
    auth_url = f"{BASE_URL}/session/v1/login-request"
    
    payload = {
        "data": {
            "CLIENT_APP_ID": "Python",
            "CLIENT_APP_VERSION": "1.0.0",
            "SVN_REVISION": "1.0.0",
            "ACCOUNT_NAME": ACCOUNT.split('.')[0],
            "LOGIN_NAME": USERNAME,
            "PASSWORD": PASSWORD,
        }
    }
    
    try:
        response = requests.post(auth_url, json=payload, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        if result.get("success"):
            return result["data"]["token"]
        else:
            print(f"Auth failed: {result.get('message', 'Unknown error')}")
            sys.exit(1)
            
    except Exception as e:
        print(f"Authentication error: {e}")
        sys.exit(1)


def make_mcp_call(method, params=None):
    """Make MCP API call to Snowflake"""
    
    # Get auth token
    token = get_auth_token()
    
    # MCP endpoint as per official docs
    endpoint = f"/api/v2/databases/{quote(DATABASE)}/schemas/{quote(SCHEMA)}/mcp-servers/{quote(MCP_SERVER_NAME)}"
    url = f"{BASE_URL}{endpoint}"
    
    # JSON-RPC payload as per official docs
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": method,
        "params": params or {}
    }
    
    headers = {
        "Authorization": f"Snowflake Token=\"{token}\"",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    
    try:
        print(f"Making {method} call to MCP server...")
        print(f"URL: {url}")
        print(f"Payload: {json.dumps(payload, indent=2)}")
        
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:500]}...")
        
        if response.status_code < 400:
            result = response.json()
            
            print("\nSUCCESS!")
            print(json.dumps(result, indent=2))
            return result
        else:
            print(f"\nFAILED: HTTP {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"\nERROR: {e}")
        return None

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python simple_mcp_client.py init")
        print("  python simple_mcp_client.py list")
        print("  python simple_mcp_client.py search 'your query here'")
        print("  python simple_mcp_client.py analyst 'your question here'")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "init":
        # Initialize MCP server
        make_mcp_call("initialize")
        
    elif command == "list":
        # List available tools
        make_mcp_call("tools/list")
        
    elif command == "search":
        # Call policy-search tool
        if len(sys.argv) < 3:
            print("Please provide a search query")
            sys.exit(1)
            
        query = sys.argv[2]
        params = {
            "name": "policy-search",
            "arguments": {
                "query": query,
                "limit": 5
            }
        }
        make_mcp_call("tools/call", params)
        
    elif command == "analyst":
        # Call revenue-semantic-view tool
        if len(sys.argv) < 3:
            print("Please provide an analyst question")
            sys.exit(1)
            
        question = sys.argv[2]
        params = {
            "name": "revenue-semantic-view",
            "arguments": {
                "message": question
            }
        }
        make_mcp_call("tools/call", params)
        
    else:
        print(f"Unknown command: {command}")
        print("Available commands: init, list, search, analyst")
        sys.exit(1)

if __name__ == "__main__":
    main()
