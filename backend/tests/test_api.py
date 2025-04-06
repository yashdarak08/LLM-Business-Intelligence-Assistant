# backend/tests/test_api.py

import pytest
from fastapi.testclient import TestClient
from backend.app import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "Welcome to the Business Intelligence Assistant API!"

def test_ingest_endpoint():
    response = client.post("/ingest")
    # Depending on the data available, this test may be adjusted.
    # For now, we assume ingestion runs without error.
    assert response.status_code == 200
    json_resp = response.json()
    assert json_resp["status"] == "success"

def test_query_endpoint_no_data():
    # Query before ingestion should lead to a 404
    response = client.post("/query", json={"query": "What are the risks?"})
    assert response.status_code == 404
    assert response.json()["detail"] == "No relevant chunks found."
    