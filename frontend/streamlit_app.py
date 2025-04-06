# frontend/streamlit_app.py

import streamlit as st
import requests
from frontend.components import charts

API_URL = "http://localhost:8000"

st.title("Business Intelligence Assistant")
st.write("Enter your business query below to receive actionable insights.")

query = st.text_input("Business Query", "")

if st.button("Get Insights"):
    if not query:
        st.warning("Please enter a query.")
    else:
        response = requests.post(f"{API_URL}/query", json={"query": query})
        if response.status_code == 200:
            data = response.json()
            st.subheader("Generated Answer")
            st.write(data["answer"])
            
            st.subheader("Retrieved Context")
            for chunk in data["retrieved_chunks"]:
                st.write(f"**Source:** {chunk.get('file_path', 'Unknown')}")
                st.write(chunk.get("text", ""))
                st.write("---")
            
            # Example of displaying a chart from the retrieved data
            charts.display_sample_chart(data["retrieved_chunks"])
        else:
            st.error(f"Error: {response.json().get('detail', 'Unknown error')}")
