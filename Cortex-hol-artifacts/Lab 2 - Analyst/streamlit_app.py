import streamlit as st
import snowflake.snowpark.context as snowpark_context
import json
import pandas as pd

# Get current Snowflake session
session = snowpark_context.get_active_session()

def ensure_session_state():
    """Ensure all required session state variables are initialized."""
    if "database" not in st.session_state:
        st.session_state.database = "CORTEX_ANALYST_DEMO"
    if "schema" not in st.session_state:
        st.session_state.schema = "WEALTH_MANAGEMENT"
    if "stage" not in st.session_state:
        st.session_state.stage = "RAW_DATA"
    if "semantic_model_file" not in st.session_state:
        st.session_state.semantic_model_file = "wealth_management.yaml"
    if "debug" not in st.session_state:
        st.session_state.debug = False

def send_message(prompt: str) -> dict:
    """Calls the REST API and returns the response."""
    # Ensure session state is properly initialized
    ensure_session_state()
    
    # Construct the semantic model file path
    semantic_model_path = f"@{st.session_state.database}.{st.session_state.schema}.{st.session_state.stage}/{st.session_state.semantic_model_file}"
    
    request_body = {
        "messages": [{"role": "user", "content": [{"type": "text", "text": prompt}]}],
        "semantic_model_file": semantic_model_path,
    }
    
    # Display debug information
    if st.session_state.debug:
        st.sidebar.text(f"Semantic Model Path: {semantic_model_path}")
        st.sidebar.text(f"Request Body: {json.dumps(request_body, indent=2)}")
    
    try:
        resp = session.sql(
            "SELECT SNOWFLAKE.CORTEX.ANALYST(parse_json(?)) as response",
            params=[json.dumps(request_body)]
        ).collect()
        
        request_id = resp[0].RESPONSE['request_id']
        
        # Display the request ID for debugging purposes
        if st.session_state.debug:
            st.sidebar.text(f"Request ID: {request_id}")
        
        return resp[0].RESPONSE
    
    except Exception as e:
        st.error(f"Error calling Cortex Analyst: {str(e)}")
        st.error(f"Semantic model path: {semantic_model_path}")
        if st.session_state.debug:
            st.error(f"Full request body: {json.dumps(request_body, indent=2)}")
        raise e

def process_message(prompt: str) -> None:
    """Processes a message and adds the response to the chat."""
    st.session_state.messages.append(
        {"role": "user", "content": [{"type": "text", "text": prompt}]}
    )
    
    with st.chat_message("user"):
        st.markdown(prompt)
    
    with st.chat_message("assistant"):
        with st.spinner("Generating response..."):
            response = send_message(prompt=prompt)
            content = response["message"]["content"]
            display_content(content=content)
    
    st.session_state.messages.append({"role": "assistant", "content": content})

def display_content(content: list, message_index: int = None) -> None:
    """Displays a content item for a message."""
    message_index = message_index or len(st.session_state.messages)
    
    for item in content:
        if item["type"] == "text":
            st.markdown(item["text"])
        elif item["type"] == "suggestions":
            with st.expander("Suggestions", expanded=True):
                for suggestion_index, suggestion in enumerate(item["suggestions"]):
                    if st.button(suggestion, key=f"{message_index}_{suggestion_index}"):
                        st.session_state.active_suggestion = suggestion
        elif item["type"] == "sql":
            with st.expander("SQL Query", expanded=False):
                st.code(item["statement"], language="sql")
            with st.expander("Results", expanded=True):
                with st.spinner("Running SQL..."):
                    try:
                        df = session.sql(item["statement"]).to_pandas()
                        if df.empty:
                            st.caption("No results")
                        else:
                            st.dataframe(df)
                    except Exception as e:
                        st.error(f"Error executing SQL: {str(e)}")
                        st.code(item["statement"], language="sql")

def page_config() -> None:
    """Configures the Streamlit page."""
    st.set_page_config(
        page_title="Wealth Management Analytics Assistant",
        page_icon="💰",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def display_sidebar() -> None:
    """Displays the sidebar configuration."""
    with st.sidebar:
        st.title("💰 Wealth Analytics")
        st.markdown("---")
        
        st.subheader("Configuration")
        if "database" not in st.session_state:
            st.session_state.database = "CORTEX_ANALYST_DEMO"
        if "schema" not in st.session_state:
            st.session_state.schema = "WEALTH_MANAGEMENT"
        if "stage" not in st.session_state:
            st.session_state.stage = "RAW_DATA"
        if "semantic_model_file" not in st.session_state:
            st.session_state.semantic_model_file = "wealth_management.yaml"
            
        st.selectbox(
            "Select database:",
            ["CORTEX_ANALYST_DEMO"],
            index=0,
            key="database"
        )
        st.selectbox(
            "Select schema:",
            ["WEALTH_MANAGEMENT"],
            index=0,
            key="schema"
        )
        st.selectbox(
            "Select stage:",
            ["RAW_DATA"],
            index=0,
            key="stage"
        )
        st.selectbox(
            "Select semantic model file:",
            ["wealth_management.yaml"],
            index=0,
            key="semantic_model_file"
        )
        
        st.markdown("---")
        st.subheader("Options")
        if "debug" not in st.session_state:
            st.session_state.debug = False
        st.checkbox("Show request ID", key="debug")
        
        st.markdown("---")
        st.subheader("Sample Questions")
        st.markdown("""
        Try asking questions like:
        
        **Portfolio Performance:**
        - What was the total portfolio value last month?
        - Which month had the highest portfolio performance?
        - Show me portfolio values by client segment
        
        **Fee Analysis:**
        - What are the total management fees this year?
        - Which client segment pays the most in fees?
        - Show me fee trends over time
        
        **Performance vs Target:**
        - How are we performing against targets?
        - Which advisor region is exceeding targets?
        - Show me clients underperforming their benchmarks
        
        **Client Insights:**
        - Which client segment has the highest portfolio value?
        - How many clients do we have by segment?
        - Show me portfolio distribution by advisor region
        """)

def main() -> None:
    """Main function for the Streamlit app."""
    page_config()
    ensure_session_state()
    display_sidebar()
    
    st.title("💰 Wealth Management Analytics Assistant")
    st.markdown("Ask questions about portfolio performance, client segments, and advisor metrics using natural language.")
    
    # Initialize chat messages
    if "messages" not in st.session_state:
        st.session_state.messages = []
        # Add welcome message
        welcome_message = {
            "role": "assistant",
            "content": [
                {
                    "type": "text",
                    "text": "👋 Welcome to the Wealth Management Analytics Assistant! I can help you analyze portfolio performance, client segments, advisor metrics, and fee structures. What would you like to know about your wealth management data?"
                },
                {
                    "type": "suggestions",
                    "suggestions": [
                        "What questions can I ask?",
                        "Show me total portfolio value by client segment",
                        "What were our management fees last quarter?",
                        "Which advisor region has the best performance?",
                        "How are we performing against our targets?"
                    ]
                }
            ]
        }
        st.session_state.messages.append(welcome_message)
    
    # Display chat messages
    for message_index, message in enumerate(st.session_state.messages):
        with st.chat_message(message["role"]):
            display_content(message["content"], message_index)
    
    # Handle active suggestion
    if "active_suggestion" in st.session_state:
        process_message(st.session_state.active_suggestion)
        del st.session_state.active_suggestion
    
    # Chat input
    if prompt := st.chat_input("Ask a question about wealth management data..."):
        process_message(prompt)

if __name__ == "__main__":
    main() 