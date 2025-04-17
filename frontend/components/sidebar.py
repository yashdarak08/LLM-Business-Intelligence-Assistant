# frontend/components/sidebar.py

import streamlit as st
import requests
import pandas as pd
import os
import time

API_URL = os.environ.get("BACKEND_URL", "http://localhost:8000")

def render_sidebar():
    """Render the sidebar with navigation and system stats."""
    with st.sidebar:
        st.title("BI Assistant")
        
        # Navigation
        st.subheader("Navigation")
        nav_options = {
            "Query Assistant": "query",
            "Document Management": "documents", 
            "Analytics Dashboard": "analytics"
        }
        
        selected_nav = st.radio("Go to:", list(nav_options.keys()))
        st.session_state.current_view = nav_options[selected_nav]
        
        st.markdown("---")
        
        # System Status
        st.subheader("System Status")
        
        if st.button("Check API Status", key="check_status"):
            try:
                with st.spinner("Checking API status..."):
                    response = requests.get(f"{API_URL}/health", timeout=5)
                    if response.status_code == 200:
                        data = response.json()
                        st.success(f"API Status: {data['status']}")
                        st.info(f"Version: {data['version']}")
                        
                        # Component status
                        components = data.get('components', {})
                        for component, status in components.items():
                            if status == "connected" or status == "loaded":
                                st.success(f"{component.capitalize()}: {status}")
                            else:
                                st.warning(f"{component.capitalize()}: {status}")
                    else:
                        st.error(f"API Error: {response.status_code}")
            except requests.exceptions.ConnectionError:
                st.error("Cannot connect to API. Is the backend running?")
            except Exception as e:
                st.error(f"Error: {str(e)}")
        
        # Document Stats
        try:
            # Only fetch stats if not done recently (cache for 30 seconds)
            if 'last_stats_time' not in st.session_state or time.time() - st.session_state.last_stats_time > 30:
                with st.spinner("Loading stats..."):
                    response = requests.get(f"{API_URL}/stats", timeout=5)
                    if response.status_code == 200:
                        st.session_state.doc_stats = response.json()
                        st.session_state.last_stats_time = time.time()
            
            # Display stats if available
            if 'doc_stats' in st.session_state:
                stats = st.session_state.doc_stats
                st.metric("Total Documents", stats["total_documents"])
                st.metric("Total Chunks", stats["total_chunks"])
                
                # Create pie chart of documents by type if available
                if stats["total_documents"] > 0:
                    # Create a simple dataframe for the chart
                    doc_data = pd.DataFrame(stats["indexed_documents"])
                    if not doc_data.empty and "chunk_count" in doc_data.columns:
                        st.caption("Chunks by Document")
                        st.bar_chart(doc_data.set_index("title")["chunk_count"])
        except:
            # Silently fail if can't fetch stats
            pass
        
        # Actions
        st.markdown("---")
        st.subheader("Actions")
        
        if st.button("Ingest Documents"):
            try:
                with st.spinner("Ingesting documents..."):
                    response = requests.post(f"{API_URL}/ingest", timeout=5)
                    if response.status_code == 200:
                        st.success("Documents ingestion started!")
                    else:
                        st.error(f"Ingestion failed: {response.json().get('detail', 'Unknown error')}")
            except Exception as e:
                st.error(f"Error: {str(e)}")
                
        # Error display (if any)
        if 'error_message' in st.session_state and st.session_state.error_message:
            st.markdown("---")
            st.error(f"Last Error: {st.session_state.error_message}")
            if st.button("Clear Error"):
                st.session_state.error_message = None
        
        # About section
        st.markdown("---")
        st.caption("Made by Yash using RAG Pipeline")