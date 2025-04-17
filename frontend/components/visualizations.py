# frontend/components/visualizations.py

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import requests
from datetime import datetime, timedelta
import time

def render_analytics_dashboard(api_url):
    """Render the analytics dashboard with visualizations."""
    st.title("Analytics Dashboard")
    st.write("Explore insights and metrics about your business intelligence system.")
    
    # Load metrics data
    try:
        metrics_response = requests.get(f"{api_url}/metrics/query", timeout=5)
        if metrics_response.status_code != 200:
            st.error(f"Failed to load metrics: {metrics_response.status_code}")
            return
            
        metrics = metrics_response.json()
        
        # Create a dashboard layout
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Queries", metrics["query_count"])
        with col2:
            st.metric("Avg Response Time", f"{metrics['average_response_time_ms']:.2f} ms")
        with col3:
            st.metric("Documents Indexed", metrics["documents_count"])
            
        # Create tabs for different visualizations
        tab1, tab2, tab3 = st.tabs(["Query Analysis", "Document Analysis", "System Performance"])
        
        with tab1:
            render_query_analysis(metrics, api_url)
            
        with tab2:
            render_document_analysis(metrics, api_url)
            
        with tab3:
            render_system_performance()
    
    except Exception as e:
        st.error(f"Error loading analytics: {str(e)}")

def render_query_analysis(metrics, api_url):
    """Render query analysis visualizations."""
    st.header("Query Analysis")
    
    # For demonstration, generate some mock query data
    # In a real application, you would fetch this from an API endpoint
    
    # Create a date range for the last 14 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=14)
    date_range = [start_date + timedelta(days=x) for x in range(15)]
    
    # Generate synthetic query counts
    np.random.seed(42)  # For reproducibility
    query_counts = np.random.poisson(lam=5, size=15).tolist()
    
    # Create a DataFrame
    query_df = pd.DataFrame({
        'date': date_range,
        'query_count': query_counts
    })
    
    # Line chart of queries over time
    st.subheader("Queries Over Time")
    fig = px.line(
        query_df, 
        x='date', 
        y='query_count',
        title='Daily Queries',
        labels={'date': 'Date', 'query_count': 'Number of Queries'}
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Mock query categories for demonstration
    # In a real application, this would come from analyzing actual queries
    categories = ["Market Analysis", "Risk Assessment", "Financial Performance", 
                 "Product Strategy", "Competitor Analysis", "Other"]
    category_counts = [15, 12, 20, 8, 10, 5]
    
    # Pie chart of query categories
    st.subheader("Query Categories")
    cat_df = pd.DataFrame({
        'category': categories,
        'count': category_counts
    })
    
    fig = px.pie(
        cat_df,
        values='count',
        names='category',
        title='Query Categories Distribution'
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Mock query response time distribution
    response_times = np.random.gamma(2, 100, 100).tolist()  # in milliseconds
    
    # Histogram of response times
    st.subheader("Response Time Distribution")
    fig = px.histogram(
        response_times,
        nbins=20,
        labels={'value': 'Response Time (ms)'},
        title='Query Response Time Distribution'
    )
    st.plotly_chart(fig, use_container_width=True)

def render_document_analysis(metrics, api_url):
    """Render document analysis visualizations."""
    st.header("Document Analysis")
    
    # Get actual document stats if available
    try:
        stats_response = requests.get(f"{api_url}/stats", timeout=5)
        if stats_response.status_code == 200:
            stats = stats_response.json()
            
            # Document count visualization
            st.subheader("Document Distribution")
            
            if stats["indexed_documents"]:
                # Create a DataFrame from the indexed documents
                docs_df = pd.DataFrame(stats["indexed_documents"])
                
                # Bar chart of chunks per document
                fig = px.bar(
                    docs_df,
                    x='title',
                    y='chunk_count',
                    title='Chunks per Document',
                    labels={'title': 'Document Title', 'chunk_count': 'Number of Chunks'}
                )
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
                
                # Document type distribution (mock data for demonstration)
                # In a real application, you would have document types in your metadata
                doc_types = ["Financial Report", "Market Research", "Strategic Plan", 
                            "Risk Analysis", "Competitive Analysis"]
                type_counts = np.random.randint(1, 5, len(doc_types)).tolist()
                
                type_df = pd.DataFrame({
                    'type': doc_types,
                    'count': type_counts
                })
                
                # Pie chart of document types
                fig = px.pie(
                    type_df,
                    values='count',
                    names='type',
                    title='Document Type Distribution'
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Document ingestion over time (mock data for demonstration)
                # In a real application, you would use actual ingestion timestamps
                end_date = datetime.now()
                dates = [end_date - timedelta(days=x) for x in range(7)]
                ingestion_counts = np.random.poisson(2, 7).tolist()
                
                ing_df = pd.DataFrame({
                    'date': dates,
                    'count': ingestion_counts
                })
                
                # Line chart of document ingestion
                fig = px.line(
                    ing_df,
                    x='date',
                    y='count',
                    title='Document Ingestion Over Time',
                    labels={'date': 'Date', 'count': 'Documents Ingested'}
                )
                st.plotly_chart(fig, use_container_width=True)
            
            else:
                st.info("No documents have been indexed yet.")
        else:
            st.error(f"Failed to load document stats: {stats_response.status_code}")
    
    except Exception as e:
        st.error(f"Error loading document analysis: {str(e)}")

def render_system_performance():
    """Render system performance visualizations."""
    st.header("System Performance")
    
    # Create mock performance data for demonstration
    # In a real application, you would pull this from monitoring endpoints
    
    # Mock CPU usage over time
    end_time = datetime.now()
    times = [end_time - timedelta(minutes=x*5) for x in range(60)]
    cpu_usage = [50 + 15*np.sin(x/5) + np.random.normal(0, 5) for x in range(60)]
    
    # Ensure values are between 0 and 100
    cpu_usage = [max(0, min(100, val)) for val in cpu_usage]
    
    perf_df = pd.DataFrame({
        'time': times,
        'cpu': cpu_usage,
        'memory': [40 + 0.5*x + np.random.normal(0, 3) for x in range(60)],
        'api_latency': [50 + 10*np.sin(x/10) + np.random.normal(0, 10) for x in range(60)]
    })
    
    # Line chart of CPU and memory usage
    st.subheader("System Resource Usage")
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=perf_df['time'],
        y=perf_df['cpu'],
        name="CPU Usage (%)"
    ))
    
    fig.add_trace(go.Scatter(
        x=perf_df['time'],
        y=perf_df['memory'],
        name="Memory Usage (%)"
    ))
    
    fig.update_layout(
        title="CPU and Memory Usage Over Time",
        xaxis_title="Time",
        yaxis_title="Usage (%)",
        legend_title="Metric"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Line chart of API latency
    st.subheader("API Latency")
    fig = px.line(
        perf_df,
        x='time',
        y='api_latency',
        title='API Response Time Over Time',
        labels={'time': 'Time', 'api_latency': 'Response Time (ms)'}
    )
    
    # Add a threshold line
    fig.add_shape(
        type="line",
        x0=perf_df['time'].min(),
        y0=100,
        x1=perf_df['time'].max(),
        y1=100,
        line=dict(
            color="Red",
            width=2,
            dash="dash",
        )
    )
    
    # Add annotation for the threshold
    fig.add_annotation(
        x=perf_df['time'].iloc[len(perf_df)//2],
        y=105,
        text="Threshold",
        showarrow=False,
        font=dict(
            color="Red"
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Mock error rate data
    error_df = pd.DataFrame({
        'date': [end_time - timedelta(days=x) for x in range(7)],
        'error_rate': [0.5 + 0.2*np.random.random() for _ in range(7)]
    })
    
    # Line chart of error rate
    st.subheader("System Error Rate")
    fig = px.line(
        error_df,
        x='date',
        y='error_rate',
        title='Daily Error Rate (%)',
        labels={'date': 'Date', 'error_rate': 'Error Rate (%)'}
    )
    st.plotly_chart(fig, use_container_width=True)