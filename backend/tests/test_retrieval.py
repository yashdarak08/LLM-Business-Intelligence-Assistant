# backend/tests/test_retrieval.py

import pytest
import numpy as np
import os
import tempfile
from unittest.mock import patch, MagicMock, mock_open
from sqlalchemy.orm import Session
from backend.retrieval import retrieve_relevant_chunks
from backend.vector_store import METADATA_STORE
from backend.database import Query, DocumentChunk, Document

@pytest.fixture
def mock_embedding_model():
    """Mock the embedding model for testing."""
    with patch("backend.retrieval.embedding_model") as mock:
        # Mock the encode method to return a simple embedding
        mock.encode.return_value = np.array([[0.1, 0.2, 0.3, 0.4, 0.5]])
        yield mock

@pytest.fixture
def mock_load_index():
    """Mock the load_index function."""
    with patch("backend.retrieval.load_index") as mock:
        # Create a mock index with a search method
        mock_index = MagicMock()
        mock_index.search.return_value = (
            np.array([[0.1, 0.2]]),  # Distances
            np.array([[0, 1]])       # Indices
        )
        mock.return_value = mock_index
        yield mock

@pytest.fixture
def mock_db_session():
    """Create a mock database session."""
    db = MagicMock(spec=Session)
    
    # Setup query function to return a MagicMock
    query_mock = MagicMock()
    db.query.return_value = query_mock
    query_mock.join.return_value = query_mock
    query_mock.filter.return_value = query_mock
    
    # Setup a mock DocumentChunk for the first query
    mock_chunk = MagicMock(spec=DocumentChunk)
    mock_chunk.id = 1
    query_mock.first.return_value = mock_chunk
    
    yield db

def test_retrieve_relevant_chunks(mock_embedding_model, mock_load_index, mock_db_session):
    """Test retrieving relevant chunks with mocked dependencies."""
    # Setup metadata store with mock data
    METADATA_STORE.clear()
    METADATA_STORE[0] = {
        "file_path": "test_doc_1.txt",
        "chunk_index": 0,
        "text": "This is test chunk 1",
        "title": "Test Document 1"
    }
    METADATA_STORE[1] = {
        "file_path": "test_doc_2.txt",
        "chunk_index": 0,
        "text": "This is test chunk 2",
        "title": "Test Document 2"
    }
    
    # Call the function
    result = retrieve_relevant_chunks("test query", mock_db_session)
    
    # Verify expected calls
    mock_embedding_model.encode.assert_called_once_with(["test query"], convert_to_numpy=True)
    mock_load_index.return_value.search.assert_called_once()
    
    # Verify query was added to database
    mock_db_session.add.assert_called()
    mock_db_session.commit.assert_called_once()
    
    # Verify the result contains metadata from the store
    assert len(result) == 2
    assert result[0]["file_path"] == "test_doc_1.txt"
    assert result[1]["file_path"] == "test_doc_2.txt"

def test_retrieve_relevant_chunks_exception(mock_embedding_model, mock_db_session):
    """Test error handling when index loading fails."""
    # Mock load_index to raise an exception
    with patch("backend.retrieval.load_index") as mock_load:
        mock_load.side_effect = FileNotFoundError("Index not found")
        
        # Verify the exception is propagated
        with pytest.raises(FileNotFoundError):
            retrieve_relevant_chunks("test query", mock_db_session)
        
        # Verify the session was rolled back
        mock_db_session.rollback.assert_called_once()

def test_retrieve_relevant_chunks_no_index():
    """Test behavior when the index file does not exist."""
    with pytest.raises(FileNotFoundError):
        retrieve_relevant_chunks("Test query")