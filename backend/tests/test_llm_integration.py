# backend/tests/test_llm_integration.py

import pytest
import json
from unittest.mock import patch, MagicMock
from backend.llm_integration import (
    generate_response, 
    generate_structured_response,
    extract_response,
    clean_response,
    get_generator
)

@pytest.fixture
def mock_generator():
    """Mock the LLM generator."""
    with patch("backend.llm_integration.get_generator") as mock:
        # Setup mock generator that returns a simple text
        generator_mock = MagicMock()
        generator_mock.return_value = [
            {"generated_text": "Test prompt\nThis is a generated response."}
        ]
        mock.return_value = generator_mock
        yield mock

@pytest.fixture
def mock_chunks():
    """Create mock document chunks."""
    return [
        {
            "file_path": "doc1.txt",
            "chunk_index": 0,
            "text": "This is document 1, chunk 0."
        },
        {
            "file_path": "doc2.txt",
            "chunk_index": 0,
            "text": "This is document 2, chunk 0."
        }
    ]

def test_extract_response():
    """Test the extract_response function to ensure it correctly removes the prompt."""
    prompt = "This is a test prompt."
    generated_text = "This is a test prompt. This is the response."
    result = extract_response(generated_text, prompt)
    assert result == "This is the response."
    
    # Test when the generated text doesn't start with the prompt
    generated_text = "Something else. This is the response."
    result = extract_response(generated_text, prompt)
    assert result == "Something else. This is the response."

def test_clean_response():
    """Test the clean_response function to ensure it trims incomplete sentences."""
    # Complete sentences
    response = "This is a complete sentence. This is another one."
    result = clean_response(response)
    assert result == "This is a complete sentence. This is another one."
    
    # Incomplete sentence at the end
    response = "This is a complete sentence. This is incomplete"
    result = clean_response(response)
    assert result == "This is a complete sentence."
    
    # No complete sentences
    response = "This is incomplete"
    result = clean_response(response)
    assert result == "This is incomplete"

def test_generate_response(mock_generator, mock_chunks):
    """Test the generate_response function."""
    query = "What is in the documents?"
    result = generate_response(query, mock_chunks)
    
    # Verify the generator was called
    mock_generator.return_value.assert_called_once()
    
    # Verify the result is correct
    assert result == "This is a generated response."

def test_generate_structured_response_success(mock_generator, mock_chunks):
    """Test the generate_structured_response function when JSON parsing succeeds."""
    # Modify the mock to return a valid JSON string
    mock_generator.return_value.return_value = [{
        "generated_text": """Test prompt
{
  "summary": "This is a test summary.",
  "key_insights": ["Insight 1", "Insight 2"],
  "recommendations": ["Recommendation 1", "Recommendation 2"],
  "sources": ["doc1.txt", "doc2.txt"]
}"""
    }]
    
    query = "What insights can you provide?"
    result = generate_structured_response(query, mock_chunks)
    
    # Verify the result is a parsed JSON object
    assert isinstance(result, dict)
    assert result["summary"] == "This is a test summary."
    assert len(result["key_insights"]) == 2
    assert len(result["recommendations"]) == 2
    assert len(result["sources"]) == 2

def test_generate_structured_response_invalid_json(mock_generator, mock_chunks):
    """Test the generate_structured_response function when JSON parsing fails."""
    # Modify the mock to return an invalid JSON string
    mock_generator.return_value.return_value = [{
        "generated_text": """Test prompt
This is not a valid JSON response.
"""
    }]
    
    with patch("backend.llm_integration.generate_response") as mock_fallback:
        mock_fallback.return_value = "Fallback response"
        
        query = "What insights can you provide?"
        result = generate_structured_response(query, mock_chunks)
        
        # Verify the fallback was called and result contains error info
        assert "error" in result
        assert result["raw_response"] == "Fallback response"
        mock_fallback.assert_called_once_with(query, mock_chunks)

def test_generate_response_exception(mock_generator, mock_chunks):
    """Test error handling in generate_response."""
    # Make the generator raise an exception
    mock_generator.return_value.side_effect = Exception("Test error")
    
    query = "What is in the documents?"
    result = generate_response(query, mock_chunks)
    
    # Verify we get an error message
    assert "I apologize" in result
    assert "Test error" in result