# Production Dockerfile for HireMind FastAPI Backend (Render / Cloud Deployment)
FROM python:3.11-slim

# Prevent Python from writing bytecode files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HF_HOME=/root/.cache/huggingface \
    PORT=8000

# Set container working directory
WORKDIR /app

# Install minimal system dependencies (curl for container health checks)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install pinned Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Pre-download and cache Sentence Transformers model ('all-MiniLM-L6-v2')
# Bakes ~90MB model weights into the image to prevent cold-start downloads
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Copy application source code, configuration, and migrations
COPY . .

# Ensure the upload directory exists for candidate resume persistence
RUN mkdir -p /app/uploads

# Expose default port
EXPOSE 8000

# Container healthcheck using FastAPI /health endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health || exit 1

# Start FastAPI using Gunicorn with 1 Uvicorn worker to conserve RAM
CMD ["sh", "-c", "gunicorn -w 1 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:${PORT:-8000}"]
