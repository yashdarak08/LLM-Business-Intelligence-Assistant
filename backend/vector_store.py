# backend/vector_store.py

import faiss
import pickle
import os
import numpy as np
import logging
from backend.config import FAISS_INDEX_PATH, EMBEDDING_DIM

logger = logging.getLogger(__name__)

# In-memory metadata store for mapping index IDs to document metadata
METADATA_STORE = {}

def create_faiss_index(dim=EMBEDDING_DIM):
    """
    Creates a FAISS index for L2 similarity search.
    """
    index = faiss.IndexFlatL2(dim)
    logger.info("Created FAISS index with dimension %d.", dim)
    return index

def add_documents_to_index(index, embeddings: np.ndarray, metadata: list):
    """
    Adds embeddings and corresponding metadata to the FAISS index.
    """
    num_embeddings = embeddings.shape[0]
    start_id = len(METADATA_STORE)
    ids = list(range(start_id, start_id + num_embeddings))
    for i, meta in zip(ids, metadata):
        METADATA_STORE[i] = meta

    index.add(embeddings)
    save_index(index, METADATA_STORE)
    logger.info("Added %d embeddings to the index.", num_embeddings)
    return index

def save_index(index, metadata, path=FAISS_INDEX_PATH):
    """
    Saves the FAISS index and metadata to disk.
    """
    faiss.write_index(index, path)
    meta_path = path + ".meta"
    with open(meta_path, "wb") as f:
        pickle.dump(metadata, f)
    logger.info("Index and metadata saved to %s.", path)

def load_index(path=FAISS_INDEX_PATH):
    """
    Loads the FAISS index and metadata from disk.
    """
    if not os.path.exists(path):
        raise FileNotFoundError("FAISS index not found. Run the ingestion process first.")
    index = faiss.read_index(path)
    meta_path = path + ".meta"
    global METADATA_STORE
    with open(meta_path, "rb") as f:
        METADATA_STORE = pickle.load(f)
    logger.info("Loaded FAISS index and metadata from %s.", path)
    return index
