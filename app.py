import sys
import os

# Add the 'src' folder to the Python path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(BASE_DIR, 'src')
sys.path.append(SRC_DIR)

# Import the LangGraph app from main_loop.py inside the src folder
from main_loop import app as langgraph_app

import streamlit as st

# Define project directories
DOCS_TO_PROCESS = os.path.join(BASE_DIR, 'docs_to_process')


# Set up page configurations
st.set_page_config(page_title="Enterprise AI Data Engine", page_icon="🤖", layout="wide")

# --- SIDEBAR: DOCUMENT INGESTION ---
with st.sidebar:
    st.header("📂 Document Ingestion")
    st.write("Upload new corporate policy PDFs here to add them to the system.")
    
    uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])
    
    if uploaded_file is not None:
        # Save the file into the folder Airflow watches
        file_path = os.path.join(DOCS_TO_PROCESS, uploaded_file.name)
        
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
            
        st.success(f"Successfully saved '{uploaded_file.name}' to ingestion folder!")
        st.info("💡 Run your Airflow DAG now to embed this file into pgvector.")

# --- MAIN INTERFACE: CHAT ASSISTANT ---
st.title("🤖 Enterprise Multi-Agent Data Assistant")
st.write("Ask questions about company operational data (SQL) or HR/corporate policies (Vector/CRAG).")

# Initialize chat history session state so messages persist on refresh
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Capture live user query input
if user_query := st.chat_input("Ask a question (e.g., 'What is the VPN policy?' or data metrics)..."):
    
    # 1. Display user message in chat
    with st.chat_message("user"):
        st.markdown(user_query)
    st.session_state.messages.append({"role": "user", "content": user_query})
    
    # 2. Call the LangGraph backend engine
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        with st.spinner("Thinking and routing query..."):
            try:
                # Invoke your actual LangGraph pipeline
                inputs = {"user_query": user_query}
                final_state = langgraph_app.invoke(inputs)
                
                # Extract response text
                ai_response = final_state.get("final_answer", "No response generated.")
                route = final_state.get("route_decision", "Unknown")
                grade = final_state.get("context_grade", "N/A")
                
                # Show helpful background routing context to the user
                debug_info = f"\n\n*⚡ System Trace: Routed via {route} | Evaluation Grade: {grade}*"
                full_output = ai_response + debug_info
                
                # Render response in UI
                response_placeholder.markdown(full_output)
                
                # Save assistant response to session history
                st.session_state.messages.append({"role": "assistant", "content": full_output})
                
            except Exception as e:
                error_msg = f"An error occurred while processing the request: {str(e)}"
                response_placeholder.error(error_msg)