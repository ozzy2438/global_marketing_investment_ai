# JARVIS AI Agency OS — Dockerfile
# =====================================
# Multi-stage ready, production-grade container
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all backend modules
COPY jarvis_core.py .
COPY jarvis_api.py .
COPY jarvis_apify_global.py .
COPY jarvis_scan_api.py .
COPY jarvis_mcp.py .
COPY jarvis_database_schema.sql .

# Copy frontend
COPY frontend/ ./frontend/

# Create data directory for SQLite persistence
RUN mkdir -p /app/data

# Expose API port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start with gunicorn in production, uvicorn in dev
CMD ["gunicorn", "jarvis_api:app", \
     "-w", "2", \
     "-k", "uvicorn.workers.UvicornWorker", \
     "--bind", "0.0.0.0:8000", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]
