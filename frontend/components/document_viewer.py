# frontend/components/document_viewer.py

import streamlit as st
import requests
import pandas as pd
import os
import time
from datetime import datetime

def render_document_manager(api_url):
    """Render the document management interface."""
    st.title("Document Management")
    
    # Tabs for different document operations
    tab1, tab2 = st.tabs(["Document Explorer", "Upload Documents"])
    
    with tab1:
        render_document_explorer(api_url)
    
    with tab2:
        render_document_uploader(api_url)

def render_document_explorer(api_url):
    """Render the document explorer interface."""
    st.header("Document Explorer")
    
    # Fetch document stats
    try:
        with st.spinner("Loading documents..."):
            response = requests.get(f"{api_url}/stats", timeout=10)
            
            if response.status_code == 200:
                stats = response.json()
                
                if stats["total_documents"] == 0:
                    st.info("No documents found. Upload documents to get started.")
                    return
                
                # Display document table
                if stats["indexed_documents"]:
                    # Convert to DataFrame for display
                    docs_df = pd.DataFrame(stats["indexed_documents"])
                    docs_df["ingestion_date"] = pd.to_datetime(docs_df["ingestion_date"])
                    
                    # Add formatted columns
                    docs_df["ingestion_date_fmt"] = docs_df["ingestion_date"].dt.strftime("%Y-%m-%d %H:%M")
                    
                    # Display as table
                    st.subheader(f"Indexed Documents ({stats['total_documents']})")
                    
                    # Display document table
                    st.dataframe(
                        docs_df[["title", "ingestion_date_fmt", "chunk_count"]].rename(
                            columns={
                                "title": "Document Title",
                                "ingestion_date_fmt": "Ingestion Date",
                                "chunk_count": "Chunks"
                            }
                        ),
                        hide_index=True
                    )
                    
                    # Document statistics
                    st.subheader("Document Statistics")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Documents", stats["total_documents"])
                    with col2:
                        st.metric("Total Chunks", stats["total_chunks"])
                    with col3:
                        st.metric("Avg. Chunks per Document", f"{stats['average_chunks_per_doc']:.2f}")
                    
                    # Interactive document viewer
                    if not docs_df.empty:
                        st.subheader("Document Viewer")
                        selected_doc = st.selectbox(
                            "Select document to view:",
                            docs_df["title"].tolist()
                        )
                        
                        # Get document details
                        doc_details = docs_df[docs_df["title"] == selected_doc].iloc[0]
                        
                        # Display document info
                        st.info(f"Document: {selected_doc}")
                        st.caption(f"Ingestion Date: {doc_details['ingestion_date_fmt']}")
                        st.caption(f"Chunks: {doc_details['chunk_count']}")
                        
                        # TODO: Add document content viewer when API supports it
                        st.warning("Full document content viewer coming soon. Currently showing chunk preview.")
                        
                        # Show sample chunks
                        with st.expander("View Document Chunks", expanded=True):
                            # Mock data for now - this would come from a real API endpoint in production
                            for i in range(min(3, doc_details["chunk_count"])):
                                st.markdown(f"**Chunk {i+1}**")
                                st.info(f"This is a preview of chunk {i+1} from document '{selected_doc}'. In a real implementation, this would show the actual chunk content from the database.")
            else:
                st.error(f"Failed to load documents: {response.status_code}")
    
    except Exception as e:
        st.error(f"Error: {str(e)}")

def render_document_uploader(api_url):
    """Render the document upload interface."""
    st.header("Upload Documents")
    
    st.write("""
    Upload your business documents to be indexed and analyzed by the system.
    Supported formats: .txt (text files)
    """)
    
    # File uploader
    uploaded_files = st.file_uploader(
        "Upload business documents", 
        type=["txt"], 
        accept_multiple_files=True
    )
    
    if uploaded_files:
        if st.button("Process Documents", type="primary"):
            with st.spinner("Processing documents..."):
                # Create data directory if it doesn't exist
                data_dir = os.environ.get("DATA_DIR", "./data")
                os.makedirs(data_dir, exist_ok=True)
                
                # Save uploaded files to data directory
                for uploaded_file in uploaded_files:
                    file_path = os.path.join(data_dir, uploaded_file.name)
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                
                # Call the ingest endpoint
                try:
                    response = requests.post(f"{api_url}/ingest", timeout=30)
                    if response.status_code == 200:
                        st.success(f"Successfully processed {len(uploaded_files)} document(s)!")
                        st.balloons()
                    else:
                        st.error(f"Failed to process documents: {response.json().get('detail', 'Unknown error')}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    else:
        st.info("Drag and drop files here to upload.")
        
    # Manual ingestion option
    with st.expander("Advanced: Manual Document Processing"):
        st.write("""
        If you've manually added documents to the data directory, you can trigger
        document ingestion without uploading through the interface.
        """)
        
        if st.button("Trigger Document Ingestion", key="manual_ingest"):
            try:
                with st.spinner("Ingesting documents..."):
                    response = requests.post(f"{api_url}/ingest", timeout=10)
                    if response.status_code == 200:
                        st.success("Document ingestion started!")
                    else:
                        st.error(f"Ingestion failed: {response.json().get('detail', 'Unknown error')}")
            except Exception as e:
                st.error(f"Error: {str(e)}")