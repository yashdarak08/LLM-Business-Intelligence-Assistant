# backend/tests/test_retrieval.py

import pytest
from backend.retrieval import retrieve_relevant_chunks

def test_retrieve_relevant_chunks_empty():
    # When no index exists or the query does not match, ensure an empty list is returned or proper exception is raised.
    with pytest.raises(FileNotFoundError):
        retrieve_relevant_chunks("Test query")
