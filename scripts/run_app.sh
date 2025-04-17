#!/bin/bash
# scripts/run_app.sh

set -e

# Change to the project root directory
cd "$(dirname "$0")/.."

# Check if running in development or production mode
MODE=${1:-dev}

# Create sample data if needed
echo "Creating sample data..."
python scripts/init_data.py

if [ "$MODE" = "dev" ]; then
    echo "Starting application in development mode..."
    
    # Setup database
    echo "Setting up database..."
    python -c "from backend.database import create_tables; create_tables()"
    
    # Start backend server
    echo "Starting backend server..."
    python -m uvicorn backend.app:app --reload --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    
    # Wait for backend to start
    echo "Waiting for backend to start..."
    sleep 5
    
    # Start frontend server
    echo "Starting frontend server..."
    BACKEND_URL=http://localhost:8000 streamlit run frontend/streamlit_app.py --server.port 8501 --server.address 0.0.0.0 &
    FRONTEND_PID=$!
    
    # Wait for both processes
    wait $BACKEND_PID $FRONTEND_PID
    
elif [ "$MODE" = "prod" ]; then
    echo "Starting application in production mode using Docker Compose..."
    docker-compose up -d
    
    echo "Application started. Services available at:"
    echo "- Frontend: http://localhost:8501"
    echo "- Backend API: http://localhost:8000"
    echo "- Prometheus: http://localhost:9090"
    echo "- Grafana: http://localhost:3000 (admin/admin)"
else
    echo "Unknown mode: $MODE"
    echo "Usage: $0 [dev|prod]"
    exit 1
fi