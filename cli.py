#!/usr/bin/env python
# cli.py

import argparse
import os
import sys
import logging
import time
import subprocess
import requests
from pathlib import Path

# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from backend.config import API_PORT, DATA_DIR
from backend.utils import ensure_data_dir_exists
from backend.database import create_tables
from backend.data_preprocessing import preprocess_and_index_documents
from backend.logging_config import setup_logging

# Configure logging
setup_logging()
logger = logging.getLogger("cli")

def start_backend():
    """Start the FastAPI backend server using Uvicorn."""
    logger.info("Starting backend server...")
    try:
        subprocess.run(
            ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", str(API_PORT)],
            check=True
        )
    except KeyboardInterrupt:
        logger.info("Backend server stopped by user.")
    except Exception as e:
        logger.error(f"Error starting backend server: {e}")
        sys.exit(1)

def start_frontend():
    """Start the Streamlit frontend server."""
    logger.info("Starting Streamlit frontend...")
    try:
        subprocess.run(
            ["streamlit", "run", "frontend/streamlit_app.py"],
            check=True
        )
    except KeyboardInterrupt:
        logger.info("Frontend server stopped by user.")
    except Exception as e:
        logger.error(f"Error starting frontend server: {e}")
        sys.exit(1)

def ingest_documents():
    """Ingest documents from the data directory."""
    logger.info("Ingesting documents...")
    ensure_data_dir_exists(DATA_DIR)
    try:
        preprocess_and_index_documents()
        logger.info("Documents ingested successfully.")
    except Exception as e:
        logger.error(f"Error ingesting documents: {e}")
        sys.exit(1)

def setup_database():
    """Set up the database and create tables."""
    logger.info("Setting up database...")
    try:
        create_tables()
        logger.info("Database tables created successfully.")
    except Exception as e:
        logger.error(f"Error setting up database: {e}")
        sys.exit(1)

def check_health():
    """Check the health of the API."""
    logger.info("Checking API health...")
    try:
        response = requests.get(f"http://localhost:{API_PORT}/health", timeout=5)
        if response.status_code == 200:
            logger.info("API is healthy.")
            print(response.json())
        else:
            logger.error(f"API health check failed: {response.status_code}")
            sys.exit(1)
    except requests.exceptions.ConnectionError:
        logger.error("Connection error: API server is not running.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error checking API health: {e}")
        sys.exit(1)

def show_stats():
    """Show document statistics."""
    logger.info("Fetching document statistics...")
    try:
        response = requests.get(f"http://localhost:{API_PORT}/stats", timeout=5)
        if response.status_code == 200:
            stats = response.json()
            print("\nDocument Statistics:")
            print(f"Total Documents: {stats['total_documents']}")
            print(f"Total Chunks: {stats['total_chunks']}")
            print(f"Average Chunks per Document: {stats['average_chunks_per_doc']:.2f}")
            
            if stats['indexed_documents']:
                print("\nIndexed Documents:")
                for doc in stats['indexed_documents']:
                    print(f"- {doc['title']} ({doc['chunk_count']} chunks)")
        else:
            logger.error(f"Failed to fetch stats: {response.status_code}")
            sys.exit(1)
    except requests.exceptions.ConnectionError:
        logger.error("Connection error: API server is not running.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error fetching stats: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Business Intelligence Assistant CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Start backend server
    start_backend_parser = subparsers.add_parser("start-backend", help="Start the backend server")
    
    # Start frontend server
    start_frontend_parser = subparsers.add_parser("start-frontend", help="Start the Streamlit frontend")
    
    # Ingest documents
    ingest_parser = subparsers.add_parser("ingest", help="Ingest documents from the data directory")
    
    # Setup database
    setup_db_parser = subparsers.add_parser("setup-db", help="Set up the database and create tables")
    
    # Health check
    health_parser = subparsers.add_parser("health", help="Check the health of the API")
    
    # Show stats
    stats_parser = subparsers.add_parser("stats", help="Show document statistics")
    
    args = parser.parse_args()
    
    if args.command == "start-backend":
        start_backend()
    elif args.command == "start-frontend":
        start_frontend()
    elif args.command == "ingest":
        ingest_documents()
    elif args.command == "setup-db":
        setup_database()
    elif args.command == "health":
        check_health()
    elif args.command == "stats":
        show_stats()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()