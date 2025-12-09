# Multi-purpose Dockerfile for the Flask app
# Small, reproducible image using slim base
FROM python:3.13-slim AS base

LABEL org.opencontainers.image.title="laba-2"
LABEL org.opencontainers.image.description="Flask app for laba-2"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# Install minimal OS deps (curl used by healthcheck, ca-certificates)
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . /app

# Create a non-root user and fix permissions
RUN groupadd -r app && useradd -r -g app app \
    && chown -R app:app /app

USER app

# Default environment variables (can be overridden by docker-compose or runtime)
ENV DATABASE_PATH=/data/my_database.db \
    FLASK_RUN_HOST=0.0.0.0 \
    FLASK_RUN_PORT=5000

EXPOSE 5000

# Lightweight healthcheck available at image level as well
HEALTHCHECK --interval=30s --timeout=5s --retries=3 CMD curl -fsS http://localhost:5000/health || exit 1

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "main:app"]
