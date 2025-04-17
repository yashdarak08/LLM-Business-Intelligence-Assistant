#!/bin/bash
# scripts/run_tests.sh

set -e

# Change to the project root directory
cd "$(dirname "$0")/.."

echo "Running tests with coverage..."
python -m pytest backend/tests/ --cov=backend --cov-report=term --cov-report=html:coverage_reports

echo "Running code quality checks..."
black --check backend/ frontend/
isort --check-only backend/ frontend/

echo "All tests and checks completed successfully!"