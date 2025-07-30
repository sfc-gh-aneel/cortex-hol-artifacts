import streamlit as st
import pandas as pd
from snowflake.snowpark.context import get_active_session
import json
from typing import List, Dict, Tuple, Optional
from snowflake.snowpark import Session
import time

# Import the internal Snowflake module for API requests
import _snowflake

# Initialize Snowpark session
session = get_active_session()

# API configuration
API_ENDPOINT = "/api/v2/cortex/analyst/message"
API_TIMEOUT = 10 * 60 * 1000  # 10 minutes in milliseconds

# Database configuration - customize these for your setup
DATABASE = "CORTEX_ANALYST_DEMO"
SCHEMA = "WEALTH_MANAGEMENT"  
STAGE = "RAW_DATA"
SEMANTIC_MODEL_FILE = "wealth_management.yaml"

# Page configuration
st.set_page_config(
    page_title="Wealth Management Analytics Assistant",
    page_icon="💰",
    layout="wide"
)

st.title("💰 Wealth Management Analytics Assistant")
st.write("Powered by Snowflake Cortex Analyst")

# Session state initialization
if "messages" not in st.session_state:
    st.session_state.messages = []
if "selected_semantic_model_path" not in st.session_state:
    st.session_state.selected_semantic_model_path = f"{DATABASE}.{SCHEMA}.{STAGE}/{SEMANTIC_MODEL_FILE}"

def get_analyst_response(messages: List[Dict]) -> Tuple[Dict, Optional[str]]:
    """
    Send chat history to the Cortex Analyst API and return the response.
    
    Args:
        messages (List[Dict]): The conversation history.
        
    Returns:
        Tuple[Dict, Optional[str]]: The response from the Cortex Analyst API and any error message.
    """
    # Prepare the request body with the user's prompt
    request_body = {
        "messages": messages,
        "semantic_model_file": f"@{st.session_state.selected_semantic_model_path}",
    }
    
    try:
        # Send a POST request to the Cortex Analyst API endpoint
        resp = _snowflake.send_snow_api_request(
            "POST",  # method
            API_ENDPOINT,  # path
            {},  # headers
            {},  # params
            request_body,  # body
            None,  # request_guid
            API_TIMEOUT,  # timeout in milliseconds
        )
        
        # Content is a string with serialized JSON object
        parsed_content = json.loads(resp["content"])
        
        # Check if the response is successful
        if resp["status"] < 400:
            # Return the content of the response as a JSON object
            return parsed_content, None
        else:
            # Craft readable error message
            error_msg = f"""
🚨 An Analyst API error has occurred 🚨

* response code: `{resp['status']}`
* request-id: `{parsed_content.get('request_id', 'N/A')}`
* error code: `{parsed_content.get('error_code', 'N/A')}`

Message: ```{parsed_content.get('message', 'Unknown error')}```
            """
            return parsed_content, error_msg
    
    except Exception as e:
        error_msg = f"""
❌ **Error calling Cortex Analyst API**: {str(e)}

**Possible solutions:**
1. Ensure Cortex Analyst is enabled in your account
2. Verify the semantic model file exists at: `@{st.session_state.selected_semantic_model_path}`
3. Check you have the CORTEX_USER database role
4. Confirm your account region supports Cortex Analyst

**To test Cortex availability, run this SQL:**
```sql
SELECT SNOWFLAKE.CORTEX.COMPLETE('snowflake-arctic', 'Hello world');
```
        """
        return {}, error_msg

def process_message(content: str) -> None:
    """
    Process a new message and get response from Cortex Analyst.
    
    Args:
        content (str): The user's message content.
    """
    # Add user message to chat history
    user_message = {
        "role": "user", 
        "content": [{"type": "text", "text": content}]
    }
    st.session_state.messages.append(user_message)
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(content)
    
    # Get response from Cortex Analyst
    with st.chat_message("assistant"):
        with st.spinner("Analyzing..."):
            # Call the Cortex Analyst API
            response, error = get_analyst_response(st.session_state.messages)
            
            if error:
                st.error(error)
                return
            
            # Extract the response content
            if "message" in response:
                assistant_message = response["message"]
                content = assistant_message.get("content", [])
                
                for item in content:
                    if item.get("type") == "text":
                        st.markdown(item.get("text", ""))
                    elif item.get("type") == "suggestions":
                        suggestions = item.get("suggestions", [])
                        if suggestions:
                            st.markdown("**Suggested follow-up questions:**")
                            for suggestion in suggestions:
                                st.markdown(f"• {suggestion}")
                    elif item.get("type") == "sql":
                        with st.expander("📊 **Generated SQL Query**", expanded=False):
                            st.code(item.get("statement", ""), language="sql")
                
                # Add assistant message to chat history
                st.session_state.messages.append(assistant_message)
                
                # Display request ID for debugging
                if "request_id" in response:
                    st.caption(f"Request ID: {response['request_id']}")
            else:
                st.error("Unexpected response format from Cortex Analyst")

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Display current semantic model
    st.markdown("**Current Semantic Model:**")
    st.code(st.session_state.selected_semantic_model_path, language="text")
    
    # Sample questions
    st.markdown("**💡 Sample Questions:**")
    sample_questions = [
        "What are the top performing portfolio values by client segment?",
        "Show me the management fees trends over time",
        "Which advisors have the highest performing portfolios?",
        "Compare portfolio performance vs targets by region",
        "What's the average portfolio value for high net worth clients?"
    ]
    
    for question in sample_questions:
        if st.button(question, key=f"sample_{hash(question)}", use_container_width=True):
            process_message(question)
    
    # Clear conversation button
    if st.button("🗑️ Clear Conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Main chat interface
st.markdown("### 💬 Chat with your wealth management data")

# Display chat history
for message in st.session_state.messages:
    role = message.get("role", "user")
    
    with st.chat_message(role):
        if role == "user":
            # Display user message
            content = message.get("content", [])
            for item in content:
                if item.get("type") == "text":
                    st.markdown(item.get("text", ""))
        else:
            # Display assistant message
            content = message.get("content", [])
            for item in content:
                if item.get("type") == "text":
                    st.markdown(item.get("text", ""))
                elif item.get("type") == "suggestions":
                    suggestions = item.get("suggestions", [])
                    if suggestions:
                        st.markdown("**Suggested follow-up questions:**")
                        for suggestion in suggestions:
                            st.markdown(f"• {suggestion}")
                elif item.get("type") == "sql":
                    with st.expander("📊 **Generated SQL Query**", expanded=False):
                        st.code(item.get("statement", ""), language="sql")

# Chat input
if prompt := st.chat_input("Ask a question about your wealth management data..."):
    process_message(prompt)

# Footer
st.markdown("---")
st.markdown("**💡 Tips:**")
st.markdown("• Ask specific questions about portfolio performance, client segments, or advisor metrics")
st.markdown("• Use time-based queries like 'last month' or 'this quarter'")
st.markdown("• Request comparisons between different client segments or advisor regions")
st.markdown("• Ask for trends, totals, averages, or breakdowns of your data") 