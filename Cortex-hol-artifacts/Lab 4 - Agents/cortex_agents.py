from typing import Any, Dict, Tuple, List, Optional
import httpx
from mcp.server.fastmcp import FastMCP
import os
import json
import uuid
from dotenv import load_dotenv
import asyncio

# Load .env file with absolute path to ensure it works when run by Claude Desktop
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
load_dotenv(env_path)

# Initialize FastMCP server
mcp = FastMCP("cortex_agent")

# Constants
SEMANTIC_MODEL_FILE = os.getenv("SEMANTIC_MODEL_FILE")
CORTEX_SEARCH_SERVICE = os.getenv("CORTEX_SEARCH_SERVICE")
SNOWFLAKE_ACCOUNT_URL = os.getenv("SNOWFLAKE_ACCOUNT_URL")
SNOWFLAKE_PAT = os.getenv("SNOWFLAKE_PAT")

if not SNOWFLAKE_PAT:
    raise RuntimeError("Set SNOWFLAKE_PAT environment variable")
if not SNOWFLAKE_ACCOUNT_URL:
    raise RuntimeError("Set SNOWFLAKE_ACCOUNT_URL environment variable")

# Headers for API requests
API_HEADERS = {
    "Authorization": f"Bearer {SNOWFLAKE_PAT}",
    "X-Snowflake-Authorization-Token-Type": "PROGRAMMATIC_ACCESS_TOKEN",
    "Content-Type": "application/json",
}

async def process_sse_response(resp: httpx.Response) -> Tuple[str, str, List[Dict]]:
    """
    Process SSE stream lines, extracting any 'delta' payloads,
    regardless of whether the JSON contains an 'event' field.
    """
    text, sql, citations = "", "", []
    async for raw_line in resp.aiter_lines():
        if not raw_line:
            continue
        raw_line = raw_line.strip()
        # only handle data lines
        if not raw_line.startswith("data:"):
            continue
        payload = raw_line[len("data:") :].strip()
        if payload in ("", "[DONE]"):
            continue
        try:
            evt = json.loads(payload)
        except json.JSONDecodeError:
            continue
        
        # Handle case where evt might be a list instead of dict
        if isinstance(evt, list):
            # If it's a list, skip or try to process each item
            continue
        elif not isinstance(evt, dict):
            continue
            
        # Check for error events first
        if "code" in evt and "message" in evt:
            error_msg = f"Snowflake API Error {evt.get('code')}: {evt.get('message')}"
            raise Exception(error_msg)
            
        # Grab the 'delta' section, whether top-level or nested in 'data'
        delta = evt.get("delta") or evt.get("data", {}).get("delta")
        if not isinstance(delta, dict):
            continue
        for item in delta.get("content", []):
            t = item.get("type")
            if t == "text":
                text += item.get("text", "")
            elif t == "tool_results":
                for result in item["tool_results"].get("content", []):
                    if result.get("type") == "json":
                        j = result["json"]
                        text += j.get("text", "")
                        # capture SQL if present
                        if "sql" in j:
                            sql = j["sql"]
                        # capture any citations
                        for s in j.get("searchResults", []):
                            citations.append({
                                "source_id": s.get("source_id"),
                                "doc_id": s.get("doc_id"),
                            })
    return text, sql, citations

async def execute_sql(sql: str) -> Dict[str, Any]:
    """Execute SQL using the Snowflake SQL API.
    
    Args:
        sql: The SQL query to execute
        
    Returns:
        Dict containing either the query results or an error message
    """
    try:
        # Generate a unique request ID
        request_id = str(uuid.uuid4())
        
        # Prepare the SQL API request
        sql_api_url = f"{SNOWFLAKE_ACCOUNT_URL}/api/v2/statements"
        sql_payload = {
            "statement": sql.replace(";", ""),
            "timeout": 60  # 60 second timeout
        }
        
        async with httpx.AsyncClient() as client:
            sql_response = await client.post(
                sql_api_url,
                json=sql_payload,
                headers=API_HEADERS,
                params={"requestId": request_id}
            )
            
            if sql_response.status_code == 200:
                return sql_response.json()
            else:
                return {"error": f"SQL API error: {sql_response.text}"}
    except Exception as e:
        return {"error": f"SQL execution error: {e}"}

import uuid
import httpx

@mcp.tool()
async def run_cortex_agents(query: str) -> Dict[str, Any]:
    """Run the Cortex agent with the given query, streaming SSE."""
    try:
        # Build your payload exactly as before
        payload = {
            "model": "claude-3-5-sonnet",
            "response_instruction": "You are a helpful AI assistant.",
            "experimental": {},
            "tools": [
                {"tool_spec": {"type": "cortex_analyst_text_to_sql", "name": "Analyst1"}},
                {"tool_spec": {"type": "cortex_search",            "name": "Search1"}},
                {"tool_spec": {"type": "sql_exec",                "name": "sql_execution_tool"}},
            ],
            "tool_resources": {
                "Analyst1": {"semantic_model_file": SEMANTIC_MODEL_FILE},
                "Search1":  {"name": CORTEX_SEARCH_SERVICE},
            },
            "tool_choice": {"type": "auto"},
            "messages": [
                {"role": "user", "content": [{"type": "text", "text": query}]}
            ],
        }

        # (Optional) generate a request ID if you want traceability
        request_id = str(uuid.uuid4())

        url = f"{SNOWFLAKE_ACCOUNT_URL}/api/v2/cortex/agent:run"
        # Copy your API headers and add the SSE Accept
        headers = {
            **API_HEADERS,
            "Accept": "text/event-stream",
        }

        # 1) Open a streaming POST
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream(
                "POST",
                url,
                json=payload,
                headers=headers,
                params={"requestId": request_id},   # SQL API needs this, Cortex agent may ignore it
            ) as resp:
                resp.raise_for_status()
                # 2) Now resp.aiter_lines() will yield each "data: …" chunk
                text, sql, citations = await process_sse_response(resp)

        # 3) If SQL was generated, execute it
        results = await execute_sql(sql) if sql else None

        # Provide informative response when no content is found
        if not text and not citations and not sql:
            text = f"I searched for information about '{query}' but didn't find any relevant content in the available documents. This could mean:\n\n1. The search service doesn't contain documents related to this topic\n2. The query might need to be rephrased\n3. The relevant information might be in a different search service\n\nPlease try a different query or check if the correct search service is configured."
        
        return {
            "text": text,
            "citations": citations,
            "sql": sql,
            "results": results,
        }
    except Exception as e:
        # Return error information in a format that Claude Desktop can handle
        error_msg = f"Error executing cortex agent query: {str(e)}"
        return {
            "text": error_msg,
            "citations": [],
            "sql": "",
            "results": None,
            "error": str(e)
        }


if __name__ == "__main__":
    mcp.run(transport='stdio')