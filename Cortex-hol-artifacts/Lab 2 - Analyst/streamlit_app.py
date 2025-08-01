import streamlit as st
import pandas as pd
from snowflake.snowpark.context import get_active_session
import json
from typing import List, Dict, Tuple, Optional
import plotly.express as px
import plotly.graph_objects as go

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

def ensure_session_state():
    """Initialize session state variables if they don't exist."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "selected_semantic_model_path" not in st.session_state:
        st.session_state.selected_semantic_model_path = f"{DATABASE}.{SCHEMA}.{STAGE}/{SEMANTIC_MODEL_FILE}"

def validate_conversation_flow(messages: List[Dict]) -> List[Dict]:
    """
    Validate and fix conversation flow to ensure roles alternate properly.
    """
    if not messages:
        return []
    
    cleaned_messages = []
    last_role = None
    
    for message in messages:
        current_role = message.get("role")
        
        # Skip consecutive messages with the same role
        if current_role != last_role:
            cleaned_messages.append(message)
            last_role = current_role
    
    return cleaned_messages

def get_analyst_response(messages: List[Dict]) -> Tuple[Dict, Optional[str]]:
    """
    Send chat history to the Cortex Analyst API and return the response.
    """
    # Validate conversation flow first
    clean_messages = validate_conversation_flow(messages)
    
    # API requires alternating roles and doesn't accept assistant messages
    # Since it doesn't maintain context, just send the most recent user message
    user_only_messages = [msg for msg in clean_messages if msg.get("role") == "user"]
    
    # Only send the most recent user message to avoid role alternation issues
    if user_only_messages:
        latest_user_message = [user_only_messages[-1]]
    else:
        latest_user_message = []
    
    # Prepare the request body with the user's prompt
    request_body = {
        "messages": latest_user_message,
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
        error_msg = f"🚨 Connection error occurred: {str(e)}"
        return {}, error_msg

def display_content(content: List[Dict], request_id: str) -> None:
    """
    Display the content from Cortex Analyst response, including executing SQL and showing results.
    """
    for item in content:
        if item.get("type") == "text":
            st.markdown(item.get("text"))
        elif item.get("type") == "suggestions":
            st.markdown("**Suggestions:**")
            suggestions = item.get("suggestions", [])
            for suggestion in suggestions:
                if st.button(suggestion, key=f"suggestion_{hash(suggestion)}_{request_id}"):
                    st.session_state.pending_question = suggestion
                    st.rerun()
        elif item.get("type") == "sql":
            sql_statement = item.get("statement", "")
            
            # Display the SQL query
            with st.expander("View SQL Query", expanded=False):
                st.code(sql_statement, language="sql")
            
            # Execute the SQL and display results
            try:
                # Execute the SQL query
                result_df = session.sql(sql_statement).to_pandas()
                
                if not result_df.empty:
                    st.subheader("Query Results")
                    st.dataframe(result_df, use_container_width=True)
                    
                    # Auto-generate visualizations based on data
                    create_visualizations(result_df, sql_statement)
                else:
                    st.info("Query executed successfully but returned no results.")
                    
            except Exception as e:
                st.error(f"Error executing SQL query: {str(e)}")
                st.code(sql_statement, language="sql")

def create_visualizations(df: pd.DataFrame, sql_query: str) -> None:
    """
    Create appropriate visualizations based on the dataframe content.
    """
    if df.empty:
        return
    
    st.subheader("📊 Data Visualization")
    
    # Get numeric and categorical columns
    numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    date_cols = df.select_dtypes(include=['datetime64']).columns.tolist()
    
    # If we have both categorical and numeric columns, create charts
    if len(numeric_cols) > 0:
        
        # Time series chart if date column exists
        if date_cols and len(numeric_cols) >= 1:
            date_col = date_cols[0]
            numeric_col = numeric_cols[0]
            
            # Sort by date for proper time series
            df_sorted = df.sort_values(by=date_col)
            
            fig_time = px.line(df_sorted, x=date_col, y=numeric_col, 
                              title=f"{numeric_col} Over Time")
            st.plotly_chart(fig_time, use_container_width=True)
        
        # Bar chart for categorical vs numeric
        if len(categorical_cols) >= 1 and len(numeric_cols) >= 1:
            cat_col = categorical_cols[0]
            num_col = numeric_cols[0]
            
            # Clean the categorical data to handle whitespace and case issues
            df_clean = df.copy()
            df_clean[cat_col] = df_clean[cat_col].astype(str).str.strip().str.title()
            
            # Aggregate data if needed
            if len(df_clean) > 20:  # If too many rows, aggregate
                agg_df = df_clean.groupby(cat_col)[num_col].sum().reset_index()
            else:
                agg_df = df_clean
            
            fig_bar = px.bar(agg_df, x=cat_col, y=num_col, 
                            title=f"{num_col} by {cat_col}")
            fig_bar.update_xaxes(tickangle=45)
            st.plotly_chart(fig_bar, use_container_width=True)
        
        # Multiple numeric columns - correlation or comparison
        if len(numeric_cols) >= 2:
            col1, col2 = st.columns(2)
            
            with col1:
                # Scatter plot for first two numeric columns
                fig_scatter = px.scatter(df, x=numeric_cols[0], y=numeric_cols[1],
                                       title=f"{numeric_cols[1]} vs {numeric_cols[0]}")
                st.plotly_chart(fig_scatter, use_container_width=True)
            
            with col2:
                # Summary statistics
                st.write("**Summary Statistics**")
                st.dataframe(df[numeric_cols].describe())
        
        # Pie chart for categorical data if appropriate
        if len(categorical_cols) >= 1 and len(df[categorical_cols[0]].unique()) <= 10:
            cat_col = categorical_cols[0]
            
            # Clean the categorical data to handle whitespace and case issues
            df_clean = df.copy()
            df_clean[cat_col] = df_clean[cat_col].astype(str).str.strip().str.title()
            
            value_counts = df_clean[cat_col].value_counts()
            
            fig_pie = px.pie(values=value_counts.values, names=value_counts.index,
                           title=f"Distribution of {cat_col}")
            st.plotly_chart(fig_pie, use_container_width=True)

def process_message(content: str) -> None:
    """
    Process a new message and get response from Cortex Analyst.
    """
    ensure_session_state()
    
    # Validate that we don't add consecutive user messages
    if (st.session_state.messages and 
        st.session_state.messages[-1].get("role") == "user"):
        # Remove the last user message to avoid consecutive user messages
        st.session_state.messages.pop()
    
    # Add user message to chat history
    user_message = {
        "role": "user", 
        "content": [{"type": "text", "text": content}]
    }
    
    # Display user message
    with st.chat_message("user"):
        st.markdown(content)
    
    # Get response from Cortex Analyst
    with st.chat_message("assistant"):
        with st.spinner("Analyzing your wealth management data..."):
            # Create temporary messages for API call
            temp_messages = st.session_state.messages + [user_message]
            
            # Call the Cortex Analyst API
            response, error = get_analyst_response(temp_messages)
            
            if error:
                st.error(error)
                return
            
            # Extract the response content
            response_content = response.get("message", {}).get("content", [])
            request_id = response.get("request_id", "")
            
            if response_content:
                # Display the response (including executing SQL and showing results)
                display_content(response_content, request_id)
                
                # Add both messages to session state only after successful response
                st.session_state.messages.append(user_message)
                assistant_message = {
                    "role": "assistant",
                    "content": response_content
                }
                st.session_state.messages.append(assistant_message)
            else:
                st.error("No content received from Cortex Analyst")

# Main UI
def main():
    st.title("💼 Wealth Management Analytics Assistant")
    st.write("Ask questions about your wealth management data using natural language")
    
    ensure_session_state()
    
    # Sidebar with information and sample questions
    with st.sidebar:
        st.header("🎯 Sample Questions")
        st.write("Try asking these questions:")
        
        sample_questions = [
            "What's the total portfolio value by client segment?",
            "Show me the trend of management fees over the last month",
            "Which advisors have the highest average portfolio performance?",
            "What's the average portfolio value for High Net Worth clients?",
            "How does performance vs target vary by advisor region?",
            "Show me clients with portfolio values above $2 million",
            "What's the distribution of client segments?",
            "Which region has the most advisors with over 10 years experience?"
        ]
        
        for question in sample_questions:
            if st.button(question, key=f"sample_{hash(question)}", use_container_width=True):
                st.session_state.pending_question = question
                st.rerun()
        
        st.divider()
        
        # Configuration info
        st.subheader("ℹ️ Configuration")
        st.text(f"Database: {DATABASE}")
        st.text(f"Schema: {SCHEMA}")
        st.text(f"Semantic Model: {SEMANTIC_MODEL_FILE}")
        
        # Clear conversation button
        if st.button("🗑️ Clear Conversation", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
        
        # Debug section (collapsible)
        with st.expander("🔧 Debug Info", expanded=False):
            st.markdown("**Conversation Structure:**")
            if st.session_state.messages:
                for i, msg in enumerate(st.session_state.messages):
                    role = msg.get("role", "unknown")
                    st.caption(f"Message {i+1}: {role}")
            else:
                st.caption("No messages in conversation")
            
            st.markdown(f"**Total messages:** {len(st.session_state.messages)}")
            st.markdown(f"**Semantic model:** @{st.session_state.selected_semantic_model_path}")
    
    # Display conversation history
    for message in st.session_state.messages:
        role = message.get("role")
        content = message.get("content", [])
        
        with st.chat_message(role):
            if role == "user":
                # Display user message
                for item in content:
                    if item.get("type") == "text":
                        st.markdown(item.get("text"))
            else:
                # Display assistant message with all content
                display_content(content, "history")
    
    # Handle pending questions from sample buttons
    if "pending_question" in st.session_state:
        question = st.session_state.pending_question
        del st.session_state.pending_question
        process_message(question)
    
    # Chat input
    if prompt := st.chat_input("Ask a question about your wealth management data..."):
        process_message(prompt)

if __name__ == "__main__":
    main() 