# backend/vector_store.py

import faiss
import pickle
import os
import numpy as np
import logging
from threading import Lock
from pathlib import Path
from backend.config import FAISS_INDEX_PATH, EMBEDDING_DIM

logger = logging.getLogger(__name__)

# In-memory metadata store for mapping index IDs to document metadata
METADATA_STORE = {}

# Lock for thread-safe access to the index
index_lock = Lock()

def create_faiss_index(dim=EMBEDDING_DIM):
    """
    Creates a FAISS index for L2 similarity search.
    If an index already exists, it loads it instead.
    """
    with index_lock:
        index_path = Path(FAISS_INDEX_PATH)
        meta_path = Path(f"{FAISS_INDEX_PATH}.meta")
        
        if index_path.exists() and meta_path.exists():
            logger.info("FAISS index already exists. Loading existing index.")
            return load_index()
        
        # Create a new index
        index = faiss.IndexFlatL2(dim)
        logger.info("Created new FAISS index with dimension %d.", dim)
        
        # Create parent directory if it doesn't exist
        index_path.parent.mkdir(parents=True, exist_ok=True)
        
        return index

def add_documents_to_index(index, embeddings: np.ndarray, metadata: list):
    """
    Adds embeddings and corresponding metadata to the FAISS index.
    Returns a list of assigned IDs.
    """
    with index_lock:
        num_embeddings = embeddings.shape[0]
        start_id = len(METADATA_STORE)
        ids = np.array(list(range(start_id, start_id + num_embeddings)), dtype=np.int64)
        
        # Update metadata store
        for i, meta in zip(ids, metadata):
            METADATA_STORE[int(i)] = meta
        
        # Add vectors to index
        index.add(embeddings)
        
        # Save index and metadata
        save_index(index, METADATA_STORE)
        
        logger.info("Added %d embeddings to the index.", num_embeddings)
        return ids.tolist()

def save_index(index, metadata, path=FAISS_INDEX_PATH):
    """
    Saves the FAISS index and metadata to disk.
    """
    with index_lock:
        try:
            path_obj = Path(path)
            path_obj.parent.mkdir(parents=True, exist_ok=True)
            
            # Create temporary files first, then rename them to avoid corruption
            temp_index_path = f"{path}.temp"
            temp_meta_path = f"{path}.meta.temp"
            
            faiss.write_index(index, temp_index_path)
            with open(temp_meta_path, "wb") as f:
                pickle.dump(metadata, f)
            
            # Rename temporary files to their final names
            os.replace(temp_index_path, path)
            os.replace(temp_meta_path, f"{path}.meta")
            
            logger.info("Index and metadata saved to %s.", path)
        except Exception as e:
            logger.error(f"Error saving index and metadata: {e}")
            raise

def load_index(path=FAISS_INDEX_PATH):
    """
    Loads the FAISS index and metadata from disk.
    """
    with index_lock:
        if not os.path.exists(path):
            raise FileNotFoundError(f"FAISS index not found at {path}. Run the ingestion process first.")
        
        meta_path = f"{path}.meta"
        if not os.path.exists(meta_path):
            raise FileNotFoundError(f"Metadata file not found at {meta_path}.")
        
        try:
            index = faiss.read_index(path)
            
            # Load metadata
            global METADATA_STORE
            with open(meta_path, "rb") as f:
                METADATA_STORE = pickle.load(f)
            
            logger.info("Loaded FAISS index and metadata from %s.", path)
            return index
        except Exception as e:
            logger.error(f"Error loading index and metadata: {e}")
            raise

def get_metadata_by_id(idx):
    """
    Returns metadata for a given index ID.
    """
    return METADATA_STORE.get(idx, {})

def search_index(index, query_embedding, top_k=5):
    """
    Searches the index for the closest vectors to the query embedding.
    Returns distances, indices, and metadata.
    """
    with index_lock:
        if index.ntotal == 0:
            logger.warning("Index is empty. No results can be returned.")
            return [], [], []
        
        # Perform the search
        distances, indices = index.search(query_embedding, min(top_k, index.ntotal))
        
        # Flatten the results (they come in a 2D array)
        distances = distances[0].tolist()
        indices = indices[0].tolist()
        
        # Get metadata for each result
        metadata_list = [get_metadata_by_id(idx) for idx in indices]
        
        return distances, indices, metadata_list