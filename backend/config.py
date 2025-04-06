# backend/config.py

# General configuration settings for the project

# FAISS index configuration
FAISS_INDEX_PATH = "./backend/faiss_index.index"
EMBEDDING_DIM = 768  # Embedding dimension for the chosen SentenceTransformer

# Model configuration
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"  # Can be replaced with a business-tuned model if available
LLM_MODEL_NAME = "gpt2"  # Replace with a business-adapted LLM if available

# Retrieval configuration
MAX_RETRIEVED_CHUNKS = 5

# API configuration
API_PORT = 8000

# Data directory for business documents
DATA_DIR = "./data"

# Logging configuration
LOG_LEVEL = "INFO"
LOG_FILE = "./backend/app.log"

# Monitoring configuration
METRICS_ENDPOINT = "/metrics"
METRICS_PORT = 9100
# Monitoring interval in seconds
MONITORING_INTERVAL = 60 
# Monitoring threshold for performance metrics
MONITORING_THRESHOLD = 0.8 