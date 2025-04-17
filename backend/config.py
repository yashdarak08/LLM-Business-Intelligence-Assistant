# backend/config.py

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# FAISS index configuration
FAISS_INDEX_PATH = os.getenv("FAISS_INDEX_PATH", "./backend/faiss_index.index")
EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", "768"))  # Embedding dimension for the chosen SentenceTransformer

# Model configuration
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "all-MiniLM-L6-v2")
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "gpt2")
LLM_MAX_LENGTH = int(os.getenv("LLM_MAX_LENGTH", "250"))

# Retrieval configuration
MAX_RETRIEVED_CHUNKS = int(os.getenv("MAX_RETRIEVED_CHUNKS", "5"))

# API configuration
API_PORT = int(os.getenv("API_PORT", "8000"))

# Data directory for business documents
DATA_DIR = os.getenv("DATA_DIR", "./data")

# Logging configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "./backend/app.log")

# Monitoring configuration
METRICS_ENDPOINT = "/metrics"
METRICS_PORT = int(os.getenv("METRICS_PORT", "9100"))
# Monitoring interval in seconds
MONITORING_INTERVAL = int(os.getenv("MONITORING_INTERVAL", "60"))
# Monitoring threshold for performance metrics
MONITORING_THRESHOLD = float(os.getenv("MONITORING_THRESHOLD", "0.8"))

# Database configuration
DB_HOST = os.getenv("DB_HOST", "db")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_USER = os.getenv("DB_USER", "user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_NAME = os.getenv("DB_NAME", "bi_db")
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"