# backend/data_preprocessing.py

import os
import glob
import nltk
import numpy as np
import logging
from datetime import datetime
from sentence_transformers import SentenceTransformer
from sqlalchemy.orm import Session
from backend.config import DATA_DIR, EMBEDDING_MODEL_NAME
from backend.vector_store import create_faiss_index, add_documents_to_index
from backend.database import Document, DocumentChunk, get_db, create_tables
from backend.utils import ensure_data_dir_exists
from tenacity import retry, stop_after_attempt, wait_exponential

logger = logging.getLogger(__name__)

# Ensure required nltk packages are downloaded
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download("punkt", quiet=True)

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
def load_embedding_model():
    """Load the sentence transformer model with retry logic."""
    try:
        return SentenceTransformer(EMBEDDING_MODEL_NAME)
    except Exception as e:
        logger.error(f"Error loading embedding model: {e}")
        raise

def load_documents(data_dir=DATA_DIR):
    """
    Loads and reads text files from the specified directory.
    For demonstration, this function reads .txt files.
    """
    ensure_data_dir_exists(data_dir)
    documents = []
    file_paths = glob.glob(os.path.join(data_dir, "*.txt"))
    logger.info(f"Found {len(file_paths)} document(s) in {data_dir}.")
    
    for file in file_paths:
        try:
            with open(file, "r", encoding="utf-8") as f:
                text = f.read()
                documents.append({
                    "file_path": file,
                    "content": text,
                    "title": os.path.basename(file),
                    "source": "file_upload",
                    "document_type": "text"
                })
        except Exception as e:
            logger.error(f"Error reading {file}: {e}")
    
    return documents

def chunk_document(text, max_chunk_size=300, min_chunk_size=50, overlap=20):
    """
    Splits a large document into smaller chunks (by sentences) for indexing.
    Includes overlap between chunks to maintain context.
    """
    sentences = nltk.sent_tokenize(text)
    chunks = []
    current_chunk = ""
    
    for sentence in sentences:
        # If adding this sentence would make the chunk too large
        if len(current_chunk.split()) + len(sentence.split()) > max_chunk_size:
            # Only add chunk if it's not too small
            if len(current_chunk.split()) >= min_chunk_size:
                chunks.append(current_chunk.strip())
            
            # Start new chunk with overlap from the end of the previous chunk
            if overlap > 0 and current_chunk:
                # Get last few sentences for overlap
                overlap_text = " ".join(current_chunk.split()[-overlap:])
                current_chunk = overlap_text + " " + sentence
            else:
                current_chunk = sentence
        else:
            current_chunk += " " + sentence
    
    # Add the last chunk if it's not too small
    if current_chunk and len(current_chunk.split()) >= min_chunk_size:
        chunks.append(current_chunk.strip())
    
    return chunks

def preprocess_and_index_documents():
    """
    Loads documents, splits them into chunks, computes embeddings, and indexes them using FAISS.
    Also stores document and chunk metadata in the database.
    """
    # Create database tables if they don't exist
    create_tables()
    
    # Get database session
    db = next(get_db())
    
    try:
        # Load documents
        docs = load_documents()
        
        if not docs:
            logger.warning("No documents found. Please add text files to the data directory.")
            return
        
        # Load embedding model
        model = load_embedding_model()
        
        # Initialize lists for chunks and metadata
        chunks = []
        metadata = []
        chunk_to_doc_map = {}  # Map chunk indices to document objects
        
        # Process each document
        for doc_data in docs:
            # Check if document already exists
            existing_doc = db.query(Document).filter_by(file_path=doc_data["file_path"]).first()
            
            if existing_doc:
                logger.info(f"Document {doc_data['file_path']} already exists in database.")
                continue
            
            # Create new document record
            new_doc = Document(
                file_path=doc_data["file_path"],
                title=doc_data.get("title", os.path.basename(doc_data["file_path"])),
                source=doc_data.get("source", "file_upload"),
                document_type=doc_data.get("document_type", "text"),
                ingestion_date=datetime.utcnow(),
                processed=False
            )
            
            db.add(new_doc)
            db.flush()  # Get the ID without committing
            
            # Split document into chunks
            doc_chunks = chunk_document(doc_data["content"])
            logger.info(f"Document {doc_data['file_path']} split into {len(doc_chunks)} chunk(s).")
            
            # Store each chunk
            for idx, chunk_text in enumerate(doc_chunks):
                chunk_start_idx = len(chunks)
                chunks.append(chunk_text)
                
                # Add chunk metadata
                metadata.append({
                    "file_path": doc_data["file_path"],
                    "title": doc_data.get("title", os.path.basename(doc_data["file_path"])),
                    "chunk_index": idx,
                    "text": chunk_text
                })
                
                # Create chunk record in database
                new_chunk = DocumentChunk(
                    document_id=new_doc.id,
                    chunk_index=idx,
                    text=chunk_text,
                    embedding_vector_id=chunk_start_idx  # Will be updated after indexing
                )
                
                db.add(new_chunk)
                chunk_to_doc_map[chunk_start_idx] = new_chunk
            
            # Mark document as processed
            new_doc.processed = True
        
        # Compute embeddings for all chunks
        if chunks:
            embeddings = model.encode(chunks, convert_to_numpy=True)
            
            # Create or load FAISS index and add embeddings
            index = create_faiss_index(embeddings.shape[1])
            vector_ids = add_documents_to_index(index, embeddings, metadata)
            
            # Update chunk records with vector IDs
            for i, vector_id in enumerate(vector_ids):
                if i in chunk_to_doc_map:
                    chunk_to_doc_map[i].embedding_vector_id = vector_id
            
            logger.info(f"Indexed {len(chunks)} chunks from {len(docs)} document(s).")
        
        # Commit changes to database
        db.commit()
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error during document preprocessing and indexing: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    preprocess_and_index_documents()
    logger.info("Data preprocessing and indexing completed.")