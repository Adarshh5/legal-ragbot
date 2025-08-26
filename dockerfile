# Final Dockerfile for Cloud Run
FROM python:3.11-slim AS base

# Prevent Python from writing pyc files & ensure output is flushed
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for Docker caching)
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy project files
COPY . .

# Cloud Run provides the PORT env var (default 8080)
ENV PORT=8080

# Expose port (not strictly required by Cloud Run, but good practice)
EXPOSE $PORT

# Run with Gunicorn + Uvicorn worker
CMD gunicorn -k uvicorn.workers.UvicornWorker src.main:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120
