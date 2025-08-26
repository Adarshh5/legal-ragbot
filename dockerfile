

# Dockerfile (paste to repo root)
FROM python:3.11-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install build deps (small)
RUN apt-get update && apt-get install -y --no-install-recommends gcc libpq-dev \
  && rm -rf /var/lib/apt/lists/*

# Copy only requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy app
COPY . .

# Expose port (optional)
ENV PORT=8080

# Use gunicorn with uvicorn worker for production
# Set workers=1 for small memory. Adjust if you want more.
CMD exec gunicorn -k uvicorn.workers.UvicornWorker src.main:app \
  --bind :$PORT \
  --workers 1 \
  --timeout 120
