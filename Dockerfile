# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set environment variables to avoid .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the entire project
COPY . .

# Expose port for FastAPI
EXPOSE 8000

# Run the FastAPI server on container start
CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]
