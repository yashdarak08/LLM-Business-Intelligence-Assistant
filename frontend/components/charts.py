# frontend/components/charts.py

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Download NLTK resources
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('punkt', quiet=True)
    nltk.download('stopwords', quiet=True)

def display_sample_chart(chunks):
    """
    Display a bar chart showing the length of text retrieved from each document.
    """
    if not chunks:
        st.info("No data available for visualization.")
        return
    
    # Extract data from chunks
    data = []
    for chunk in chunks:
        file_path = chunk.get("file_path", "Unknown")
        # Get filename from path
        file_name = file_path.split("/")[-1] if "/" in file_path else file_path
        text_length = len(chunk.get("text", "").split())
        data.append({"Source": file_name, "Word Count": text_length})
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Display bar chart using Plotly
    st.subheader("Text Chunk Word Count by Source")
    fig = px.bar(
        df, 
        x="Source", 
        y="Word Count",
        title="Word Count per Retrieved Chunk",
        labels={"Source": "Document Source", "Word Count": "Number of Words"}
    )
    fig.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig, use_container_width=True)
    
    # Create word cloud from text
    display_word_frequency(chunks)
    
    # Display chunk similarity visualization
    display_chunk_similarity(chunks)

def display_word_frequency(chunks, top_n=10, exclude_stopwords=True):
    """
    Display word frequency analysis from chunks.
    """
    if not chunks:
        return
    
    st.subheader("Key Terms Analysis")
    
    # Extract all text from chunks
    all_text = " ".join([chunk.get("text", "") for chunk in chunks])
    
    # Tokenize and clean text
    words = word_tokenize(all_text.lower())
    
    # Remove stopwords and punctuation
    stop_words = set(stopwords.words('english'))
    if exclude_stopwords:
        words = [word for word in words if word.isalpha() and word not in stop_words and len(word) > 2]
    else:
        words = [word for word in words if word.isalpha() and len(word) > 2]
    
    # Count word frequencies
    word_freq = Counter(words)
    
    # Get top N words
    top_words = word_freq.most_common(top_n)
    
    # Create DataFrame for visualization
    word_df = pd.DataFrame(top_words, columns=['Word', 'Frequency'])
    
    # Display horizontal bar chart
    fig = px.bar(
        word_df, 
        x='Frequency', 
        y='Word',
        orientation='h',
        title=f'Top {top_n} Words in Retrieved Chunks',
        labels={'Frequency': 'Word Count', 'Word': 'Term'}
    )
    fig.update_layout(yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig, use_container_width=True)
    
    # Option to toggle stopwords
    if st.checkbox("Include common words (stopwords)", value=not exclude_stopwords):
        display_word_frequency(chunks, top_n, not exclude_stopwords)

def display_chunk_similarity(chunks):
    """
    Display a visualization of chunk similarity/relevance.
    """
    if not chunks or len(chunks) < 2:
        return
    
    st.subheader("Document Chunk Relevance")
    
    # Create mock relevance scores for demonstration
    # In a real application, these would come from actual similarity scores
    import numpy as np
    np.random.seed(42)  # For reproducibility
    
    # Create a matrix of mock similarity scores
    n_chunks = len(chunks)
    similarity_matrix = np.zeros((n_chunks, n_chunks))
    
    for i in range(n_chunks):
        for j in range(n_chunks):
            if i == j:
                similarity_matrix[i, j] = 1.0  # Perfect self-similarity
            else:
                # Random similarity between 0.3 and 0.9
                similarity_matrix[i, j] = 0.3 + 0.6 * np.random.random()
    
    # Get chunk labels (filenames)
    chunk_labels = []
    for chunk in chunks:
        file_path = chunk.get("file_path", "Unknown")
        file_name = file_path.split("/")[-1] if "/" in file_path else file_path
        chunk_idx = chunk.get("chunk_index", 0)
        chunk_labels.append(f"{file_name} (Chunk {chunk_idx})")
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=similarity_matrix,
        x=chunk_labels,
        y=chunk_labels,
        colorscale='Viridis',
        hoverongaps=False,
        colorbar=dict(title="Similarity Score")
    ))
    
    fig.update_layout(
        title="Chunk Similarity Matrix",
        xaxis_title="Document Chunks",
        yaxis_title="Document Chunks",
        xaxis_tickangle=-45
    )
    
    st.plotly_chart(fig, use_container_width=True)
    st.caption("Note: This visualization shows the similarity between different document chunks. Higher scores (darker colors) indicate greater content similarity.")

def display_entity_chart(chunks):
    """
    Display entities extracted from the chunks.
    This is a placeholder for a more sophisticated entity extraction.
    """
    st.subheader("Named Entity Recognition")
    st.info("Coming soon: Entity extraction and visualization to identify key people, organizations, and concepts in your documents.")