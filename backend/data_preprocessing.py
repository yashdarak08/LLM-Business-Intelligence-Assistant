# backend/data_preprocessing.py

import os
import glob
import nltk
import numpy as np
import logging
from sentence_transformers import SentenceTransformer
from backend.config import DATA_DIR, EMBEDDING_MODEL_NAME
from backend.vector_store import create_faiss_index, add_documents_to_index

logger = logging.getLogger(__name__)

# Ensure required nltk packages are downloaded (e.g., for sentence tokenization)
nltk.download("punkt")

def load_documents(data_dir=DATA_DIR):
    """
    Loads and reads text files from the specified directory.
    For demonstration, this function reads .txt files.
    """
    documents = []
    file_paths = glob.glob(os.path.join(data_dir, "*.txt"))
    logger.info(f"Found {len(file_paths)} document(s) in {data_dir}.")
    for file in file_paths:
        try:
            with open(file, "r", encoding="utf-8") as f:
                text = f.read()
                documents.append({
                    "file_path": file,
                    "content": text
                })
        except Exception as e:
            logger.error(f"Error reading {file}: {e}")
    return documents

def chunk_document(text, max_chunk_size=300):
    """
    Splits a large document into smaller chunks (by sentences) for indexing.
    """
    sentences = nltk.sent_tokenize(text)
    chunks = []
    current_chunk = ""
    for sentence in sentences:
        if len(current_chunk.split()) + len(sentence.split()) > max_chunk_size:
            chunks.append(current_chunk.strip())
            current_chunk = sentence
        else:
            current_chunk += " " + sentence
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks

def preprocess_and_index_documents():
    """
    Loads documents, splits them into chunks, computes embeddings, and indexes them using FAISS.
    """
    docs = load_documents()

    if not docs:
        logger.warning("No documents found. Please add text files to the data directory.")
        return

    model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    chunks = []
    metadata = []  # To hold metadata about each chunk

    for doc in docs:
        doc_chunks = chunk_document(doc["content"])
        logger.info(f"Document {doc['file_path']} split into {len(doc_chunks)} chunk(s).")
        for idx, chunk in enumerate(doc_chunks):
            chunks.append(chunk)
            metadata.append({
                "file_path": doc["file_path"],
                "chunk_index": idx,
                "text": chunk
            })

    embeddings = model.encode(chunks, convert_to_numpy=True)
    index = create_faiss_index(embeddings.shape[1])
    add_documents_to_index(index, embeddings, metadata)

    logger.info(f"Indexed {len(chunks)} chunks from {len(docs)} document(s).")

if __name__ == "__main__":
    preprocess_and_index_documents()
    logger.info("Data preprocessing and indexing completed.")
    