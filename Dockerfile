# Dockerfile for Project Shri Sudarshan
# A Hybrid Multi-Agent LLM Architecture for Stock and Derivatives Trading

# Use Python 3.11 slim as base image
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# Set working directory
WORKDIR /app

# Install system dependencies
# Note: For GPU support, use nvidia/cuda base image instead
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file first for better caching
COPY requirements.txt pyproject.toml setup.py ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY src/ ./src/
COPY .env.example ./

# Create directories for persistent data
RUN mkdir -p /app/data/chroma_db /app/data/logs

# Add src to Python path
ENV PYTHONPATH=/app:${PYTHONPATH}

# Set default working directory to where main.py is located
WORKDIR /app/src

# Default command - can be overridden
# Usage: docker run shri-sudarshan --symbol AAPL
ENTRYPOINT ["python", "main.py"]
CMD ["--help"]

# Healthcheck (optional)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Labels
LABEL maintainer="Project Shri Sudarshan Team" \
      description="Hybrid Multi-Agent LLM Architecture for Stock and Derivatives Trading" \
      version="0.1.0"
