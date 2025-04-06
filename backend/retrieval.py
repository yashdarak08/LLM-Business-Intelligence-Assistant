# backend/retrieval.py

import logging
import numpy as np
from sentence_transformers import SentenceTransformer
from backend.config import EMBEDDING_MODEL_NAME, MAX_RETRIEVED_CHUNKS
from backend.vector_store import load_index, METADATA_STORE

logger = logging.getLogger(__name__)

# Load the embedding model (reused across queries)
embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)

def retrieve_relevant_chunks(query: str):
    """
    Given a query string, compute its embedding and retrieve the top relevant chunks
    from the FAISS index.
    """
    query_embedding = embedding_model.encode([query], convert_to_numpy=True)
    index = load_index()
    distances, indices = index.search(query_embedding, MAX_RETRIEVED_CHUNKS)
    
    retrieved = []
    for idx in indices[0]:
        if idx in METADATA_STORE:
            retrieved.append(METADATA_STORE[idx])
    logger.info("Retrieved %d chunk(s) for the query.", len(retrieved))
    return retrieved
