# frontend/components/charts.py

import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd

def display_sample_chart(chunks):
    """
    Display a sample bar chart showing the length of text retrieved from each document.
    """
    data = []
    for chunk in chunks:
        file_path = chunk.get("file_path", "Unknown")
        text_length = len(chunk.get("text", "").split())
        data.append({"Source": file_path, "Word Count": text_length})
    
    df = pd.DataFrame(data)
    
    st.subheader("Text Chunk Word Count by Source")
    fig, ax = plt.subplots()
    ax.bar(df["Source"], df["Word Count"])
    ax.set_xlabel("Document Source")
    ax.set_ylabel("Word Count")
    ax.set_title("Word Count per Retrieved Chunk")
    st.pyplot(fig)
