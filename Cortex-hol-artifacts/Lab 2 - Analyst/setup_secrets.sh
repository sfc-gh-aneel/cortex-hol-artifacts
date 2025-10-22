#!/bin/bash

echo "🔧 MCP Client Setup - Creating secrets.json"
echo

# Check if secrets.json already exists
if [ -f "secrets.json" ]; then
    read -p "⚠️  secrets.json already exists. Overwrite? (y/N): " overwrite
    if [[ ! "$overwrite" =~ ^[Yy]$ ]]; then
        echo "❌ Setup cancelled"
        exit 0
    fi
fi

# Get credentials interactively
echo "📝 Enter your Snowflake credentials:"
echo

read -p "Account (e.g., abc12345.us-east-1): " ACCOUNT
read -p "Database [cortex_analyst_demo]: " DATABASE
DATABASE=${DATABASE:-cortex_analyst_demo}
read -p "Schema [public]: " SCHEMA
SCHEMA=${SCHEMA:-public}
read -p "MCP Server Name [FIN_SERV_MCP]: " MCP_SERVER_NAME
MCP_SERVER_NAME=${MCP_SERVER_NAME:-FIN_SERV_MCP}
read -p "Username: " USERNAME
read -s -p "Password: " PASSWORD
echo
echo

# Create secrets.json file
cat > secrets.json << EOF
{
    "account": "$ACCOUNT",
    "database": "$DATABASE",
    "schema": "$SCHEMA", 
    "mcp_server_name": "$MCP_SERVER_NAME",
    "username": "$USERNAME",
    "password": "$PASSWORD"
}
EOF

echo "✅ Created secrets.json"
echo "🔒 This file is ignored by git (won't be committed)"
echo
echo "🚀 You can now run:"
echo "   python simple_mcp_client.py init"
echo "   python simple_mcp_client.py list"
echo "   python simple_mcp_client.py search 'your query'"
echo "   python simple_mcp_client.py analyst 'your question'"
echo
