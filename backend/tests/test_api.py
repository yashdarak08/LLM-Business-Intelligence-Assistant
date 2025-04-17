# backend/tests/test_api.py

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from sqlalchemy.orm import Session
from backend.app import app
from backend.database import Document, DocumentChunk, Base, get_db

client = TestClient(app)

# Mock dependencies
def override_get_db():
    """Mock database session for testing."""
    try:
        # Use in-memory SQLite for testing
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        
        engine = create_engine("sqlite:///:memory:")
        TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        Base.metadata.create_all(bind=engine)
        
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

# Override the dependency
app.dependency_overrides[get_db] = override_get_db

@pytest.fixture
def mock_retrieve_chunks():
    """Mock the retrieve_relevant_chunks function."""
    with patch("backend.app.retrieve_relevant_chunks") as mock:
        mock.return_value = [
            {
                "file_path": "test_document.txt",
                "chunk_index": 0,
                "text": "This is a test document chunk for testing."
            }
        ]
        yield mock

@pytest.fixture
def mock_generate_response():
    """Mock the generate_response function."""
    with patch("backend.app.generate_response") as mock:
        mock.return_value = "This is a mock response from the LLM."
        yield mock

@pytest.fixture
def mock_generate_structured_response():
    """Mock the generate_structured_response function."""
    with patch("backend.app.generate_structured_response") as mock:
        mock.return_value = {
            "summary": "Test summary",
            "key_insights": ["Insight 1", "Insight 2"],
            "recommendations": ["Recommendation 1", "Recommendation 2"],
            "sources": ["test_document.txt"]
        }
        yield mock

@pytest.fixture
def mock_preprocess():
    """Mock the preprocess_and_index_documents function."""
    with patch("backend.app.preprocess_and_index_documents") as mock:
        mock.return_value = None
        yield mock

def test_root():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    assert "Welcome to the Business Intelligence Assistant API" in response.json()["message"]

def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert "version" in response.json()
    assert "components" in response.json()

def test_ingest_endpoint(mock_preprocess):
    """Test the document ingestion endpoint."""
    response = client.post("/ingest")
    assert response.status_code == 200
    assert response.json()["status"] == "success"
    mock_preprocess.assert_called_once()

def test_query_endpoint_with_results(mock_retrieve_chunks, mock_generate_response):
    """Test the query endpoint when results are found."""
    response = client.post("/query", json={"query": "test query", "structured_output": False})
    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "test query"
    assert len(data["retrieved_chunks"]) > 0
    assert data["answer"] == "This is a mock response from the LLM."
    assert "processing_time_ms" in data
    mock_retrieve_chunks.assert_called_once_with("test query", mock_retrieve_chunks.return_value)

def test_query_endpoint_structured_output(mock_retrieve_chunks, mock_generate_structured_response):
    """Test the query endpoint with structured output."""
    response = client.post("/query", json={"query": "test query", "structured_output": True})
    assert response.status_code == 200
    data = response.json()
    assert data["query"] == "test query"
    assert len(data["retrieved_chunks"]) > 0
    assert data["answer"]["summary"] == "Test summary"
    assert len(data["answer"]["key_insights"]) == 2
    assert len(data["answer"]["recommendations"]) == 2
    mock_retrieve_chunks.assert_called_once_with("test query", mock_retrieve_chunks.return_value)

def test_query_endpoint_no_results(mock_retrieve_chunks):
    """Test the query endpoint when no results are found."""
    mock_retrieve_chunks.return_value = []
    response = client.post("/query", json={"query": "test query", "structured_output": False})
    assert response.status_code == 404
    assert "No relevant documents found" in response.json()["detail"]

def test_stats_endpoint():
    """Test the stats endpoint."""
    # Add test data
    db = next(override_get_db())
    doc = Document(file_path="test_doc.txt", title="Test Document", processed=True)
    db.add(doc)
    db.flush()
    
    chunk = DocumentChunk(document_id=doc.id, chunk_index=0, text="Test chunk")
    db.add(chunk)
    db.commit()
    
    response = client.get("/stats")
    assert response.status_code == 200
    data = response.json()
    assert data["total_documents"] == 1
    assert data["total_chunks"] == 1
    assert data["average_chunks_per_doc"] == 1.0
    assert len(data["indexed_documents"]) == 1

def test_query_metrics_endpoint():
    """Test the query metrics endpoint."""
    response = client.get("/metrics/query")
    assert response.status_code == 200
    data = response.json()
    assert "query_count" in data
    assert "average_response_time_ms" in data
    assert "documents_count" in data
    assert "chunks_count" in data