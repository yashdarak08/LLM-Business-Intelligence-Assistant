# LLM-Powered Business Intelligence Assistant

This repository contains a production-grade business intelligence assistant that leverages retrieval-augmented generation (RAG) and large language models (LLMs) to extract actionable insights from business documents.

The system is composed of:
- **Backend**: A FastAPI server that handles document ingestion, semantic indexing via FAISS, retrieval of relevant text chunks, LLM-based answer generation, logging, and Prometheus-based monitoring.
- **Frontend**: A Streamlit-based interactive UI that allows business analysts to query the system and visualize responses.
- **Deployment**: Containerization using Docker and orchestration with Docker Compose.
- **Testing**: Unit tests for API endpoints and retrieval functionality using Pytest.

``` bash
LLM-Business-Intelligence-Assistant/
├── README.md
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── backend
│   ├── __init__.py
│   ├── app.py
│   ├── config.py
│   ├── data_preprocessing.py
│   ├── llm_integration.py
│   ├── logging_config.py
│   ├── monitoring.py
│   ├── models.py
│   ├── retrieval.py
│   ├── utils.py
│   ├── vector_store.py
│   └── tests
│       ├── test_api.py
│       └── test_retrieval.py
└── frontend
    ├── streamlit_app.py
    └── components
         └── charts.py

```

## Features

- **Data Ingestion & Preprocessing**: Ingest business documents (e.g., annual reports, market research) and split them into manageable chunks.
- **Vector Store**: Index document embeddings using FAISS for semantic similarity search.
- **RAG Pipeline**: Retrieve relevant document chunks and use an LLM (via HuggingFace Transformers) to generate actionable insights.
- **Logging & Monitoring**: Robust logging configuration and Prometheus integration for monitoring API metrics.
- **Interactive UI**: A Streamlit frontend with chart components to display query results.
- **Testing**: Unit tests to ensure code quality and endpoint reliability.

## Getting Started

### Prerequisites

- Python 3.8+
- Docker (for containerized deployment)

### Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/yourusername/LLM-Business-Intelligence-Assistant.git
   cd LLM-Business-Intelligence-Assistant

    ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ``` 

