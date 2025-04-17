# backend/retrieval.py

import logging
import time
import numpy as np
from datetime import datetime
from sentence_transformers import SentenceTransformer
from sqlalchemy.orm import Session
from backend.config import EMBEDDING_MODEL_NAME, MAX_RETRIEVED_CHUNKS
from backend.vector_store import load_index, search_index
from backend.database import Query, QueryChunk, DocumentChunk, get_db

logger = logging.getLogger(__name__)

# Load the embedding model (reused across queries)
embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)

def retrieve_relevant_chunks(query: str, db: Session = None):
    """
    Given a query string, compute its embedding and retrieve the top relevant chunks
    from the FAISS index. Also records the query and retrieval information in the database.
    """
    start_time = time.time()
    
    # Get database session if not provided
    close_db = False
    if db is None:
        db = next(get_db())
        close_db = True
    
    try:
        # Create query record
        query_record = Query(query_text=query, timestamp=datetime.utcnow())
        db.add(query_record)
        db.flush()  # Get the ID without committing
        
        # Compute query embedding
        query_embedding = embedding_model.encode([query], convert_to_numpy=True)
        
        # Load index and search
        try:
            index = load_index()
            distances, indices, retrieved_metadata = search_index(
                index, query_embedding, top_k=MAX_RETRIEVED_CHUNKS
            )
        except FileNotFoundError as e:
            logger.error(f"Index not found: {e}")
            raise
        except Exception as e:
            logger.error(f"Error during retrieval: {e}")
            raise
        
        # Record retrieval information
        for i, (distance, idx, metadata) in enumerate(zip(distances, indices, retrieved_metadata)):
            # Find the corresponding DocumentChunk
            file_path = metadata.get("file_path")
            chunk_index = metadata.get("chunk_index")
            
            doc_chunk = db.query(DocumentChunk).join(
                DocumentChunk.document
            ).filter(
                DocumentChunk.chunk_index == chunk_index,
                DocumentChunk.document.has(file_path=file_path)
            ).first()
            
            if doc_chunk:
                # Add query-chunk relationship
                query_chunk = QueryChunk(
                    query_id=query_record.id,
                    chunk_id=doc_chunk.id,
                    relevance_score=float(1.0 / (1.0 + distance))  # Convert distance to similarity score
                )
                db.add(query_chunk)
        
        # Record response time
        end_time = time.time()
        query_record.response_time = (end_time - start_time) * 1000  # Convert to milliseconds
        
        # Commit changes
        db.commit()
        
        logger.info("Retrieved %d chunk(s) for the query: %s", len(retrieved_metadata), query)
        return retrieved_metadata
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error during retrieval: {e}")
        raise
    finally:
        if close_db:
            db.close()