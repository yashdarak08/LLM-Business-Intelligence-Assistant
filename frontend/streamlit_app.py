# frontend/streamlit_app.py

import streamlit as st
import requests
import pandas as pd
import json
import time
import os
from datetime import datetime
from frontend.components import charts, sidebar, visualizations, document_viewer

# Get backend URL from environment variable or use default
API_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")

# Page configuration
st.set_page_config(
    page_title="Business Intelligence Assistant",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if "query_history" not in st.session_state:
    st.session_state.query_history = []
if "documents" not in st.session_state:
    st.session_state.documents = []
if "current_view" not in st.session_state:
    st.session_state.current_view = "query"
if "error_message" not in st.session_state:
    st.session_state.error_message = None

# Sidebar with navigation and stats
sidebar.render_sidebar()

# Main content area
if st.session_state.current_view == "query":
    # Business Intelligence Query Interface
    st.title("Business Intelligence Assistant")
    st.write("""
    Enter your business query below to receive actionable insights from your documents.
    Our system uses semantic search and large language models to analyze your business data.
    """)
    
    # Query input
    query = st.text_area("Business Query", height=100, 
                         placeholder="Example: What are the key risks identified in our quarterly reports?")
    
    col1, col2 = st.columns([1, 3])
    with col1:
        use_structured_output = st.checkbox("Use structured output format", value=True)
    with col2:
        if st.button("Get Insights", type="primary", disabled=not query):
            with st.spinner("Processing your query..."):
                try:
                    # Call API
                    response = requests.post(
                        f"{API_URL}/query", 
                        json={"query": query, "structured_output": use_structured_output},
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        # Store in history
                        st.session_state.query_history.append({
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "query": query,
                            "response": data
                        })
                        
                        # Display response
                        st.subheader("Generated Answer")
                        
                        if use_structured_output and isinstance(data["answer"], dict):
                            # Display structured response
                            answer = data["answer"]
                            
                            st.markdown(f"### Summary")
                            st.markdown(answer.get("summary", "No summary provided"))
                            
                            st.markdown(f"### Key Insights")
                            for insight in answer.get("key_insights", []):
                                st.markdown(f"- {insight}")
                            
                            st.markdown(f"### Recommendations")
                            for rec in answer.get("recommendations", []):
                                st.markdown(f"- {rec}")
                            
                            if "sources" in answer and answer["sources"]:
                                st.markdown(f"### Sources")
                                for source in answer["sources"]:
                                    st.markdown(f"- {source}")
                        else:
                            # Display unstructured response
                            st.write(data["answer"])
                        
                        # Retrieved Context section
                        with st.expander("View Source Documents", expanded=False):
                            st.subheader("Retrieved Context")
                            for i, chunk in enumerate(data["retrieved_chunks"]):
                                st.markdown(f"**Source {i+1}:** {chunk.get('file_path', 'Unknown')}")
                                st.markdown(f"**Excerpt:**")
                                st.info(chunk.get("text", ""))
                        
                        # Display visualization of the retrieved data
                        st.subheader("Data Visualization")
                        charts.display_sample_chart(data["retrieved_chunks"])
                        
                        # Processing time
                        if "processing_time_ms" in data:
                            st.caption(f"Processing time: {data['processing_time_ms']:.2f} ms")
                    
                    else:
                        error_detail = response.json().get("detail", "Unknown error")
                        st.error(f"Error: {error_detail}")
                        st.session_state.error_message = error_detail
                        
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
                    st.session_state.error_message = str(e)
    
    # Display query history if available
    if st.session_state.query_history:
        with st.expander("Query History", expanded=False):
            for i, item in enumerate(reversed(st.session_state.query_history)):
                st.markdown(f"**Query {len(st.session_state.query_history) - i}:** {item['query']} ({item['timestamp']})")
                if st.button(f"View Results #{len(st.session_state.query_history) - i}", key=f"hist_{i}"):
                    st.json(item['response'])
                st.markdown("---")

elif st.session_state.current_view == "documents":
    # Document Management Interface
    document_viewer.render_document_manager(API_URL)

elif st.session_state.current_view == "analytics":
    # Analytics Dashboard
    visualizations.render_analytics_dashboard(API_URL)

# Footer
st.markdown("---")
st.caption("Business Intelligence Assistant © 2024 - Powered by RAG and LLMs")