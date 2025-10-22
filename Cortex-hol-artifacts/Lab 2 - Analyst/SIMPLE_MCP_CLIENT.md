# 🎯 Simple MCP Client 

**Dead simple tools to call your Snowflake MCP server directly**

Based on official docs: https://docs.snowflake.com/en/user-guide/snowflake-cortex/cortex-agents-mcp#initialize-the-mcp-server

---

## 🚀 **Two Options Available**

### **Option 1: Python Script** (Recommended)
```bash
cd "Lab 2 - Analyst"
python simple_mcp_client.py init
python simple_mcp_client.py list  
python simple_mcp_client.py search "retirement plan documents"
python simple_mcp_client.py analyst "What's the total portfolio value?"
```

### **Option 2: Bash/curl Script**  
```bash
cd "Lab 2 - Analyst"
./mcp_curl_commands.sh init
./mcp_curl_commands.sh list
./mcp_curl_commands.sh search "retirement plan documents" 
./mcp_curl_commands.sh analyst "What's the total portfolio value?"
```

---

## 📝 **What Each Command Does**

### **`init`** - Initialize MCP Server
- **API Call**: `POST /api/v2/databases/{db}/schemas/{schema}/mcp-servers/{name}`
- **Method**: `initialize`
- **Purpose**: Establish connection to your MCP server

### **`list`** - List Available Tools  
- **API Call**: Same endpoint  
- **Method**: `tools/list`
- **Purpose**: Show policy-search and revenue-semantic-view tools

### **`search`** - Call Policy Search Tool
- **API Call**: Same endpoint
- **Method**: `tools/call` 
- **Tool**: `policy-search`
- **Purpose**: Search retirement plan documents using Cortex Search

### **`analyst`** - Call Analyst Tool
- **API Call**: Same endpoint
- **Method**: `tools/call`
- **Tool**: `revenue-semantic-view`  
- **Purpose**: Query wealth management data using Cortex Analyst

---

## 🔧 **One-Time Setup**

### **Step 1: Create secrets.json (once only)**
```bash
cd "Lab 2 - Analyst"
./setup_secrets.sh
```
Enter your Snowflake credentials - they'll be stored in `secrets.json` (git-ignored).

### **Step 2: Requirements**
- **Python**: `pip install requests` 
- **Bash version**: `brew install jq` (for JSON parsing)

### **Step 3: Your MCP Server Components**
Make sure you have:
- MCP server created (`FIN_SERV_MCP`)
- Cortex Search Service (`DOCUMENT_SEARCH_SERVICE`) 
- Semantic model file (`wealth_management.yaml`)

---

## 💡 **Examples**

```bash
# Initialize the connection
python simple_mcp_client.py init

# See what tools are available
python simple_mcp_client.py list

# Search for salary reduction info
python simple_mcp_client.py search "salary reduction agreement requirements"

# Ask analyst questions
python simple_mcp_client.py analyst "Show me portfolio performance by client segment"
python simple_mcp_client.py analyst "What are the average management fees?"
```

---

## 🎊 **This Actually Works**

- **No Streamlit complexity**
- **No fake UDFs**
- **No mock data**  
- **Direct HTTP calls** to Snowflake MCP API as documented
- **Real JSON-RPC** requests exactly as specified
- **Actual MCP server execution**

**These tools make the exact API calls shown in the official Snowflake documentation.** 🚀
