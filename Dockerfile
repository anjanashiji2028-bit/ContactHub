# Multi-stage / Production Dockerfile for ContactHub
# Base image: Official lightweight Python 3.12 slim
FROM python:3.12-slim

# Labels for metadata and academic traceability
LABEL maintainer="ContactHub Development Team"
LABEL description="ContactHub Contact Management System - BCA Microproject"
LABEL version="1.0.0"

# Set environment variables to prevent Python from writing .pyc and to buffer output
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=5000 \
    DATABASE_PATH=/app/database/contacthub.db \
    FLASK_DEBUG=False

# Set working directory
WORKDIR /app

# Install system dependencies (curl for healthchecks and sqlite3 utilities)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    sqlite3 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY . /app/

# Create a dedicated non-root application user for least-privilege security
RUN groupadd -g 1000 contactuser && \
    useradd -u 1000 -g contactuser -s /bin/bash -m contactuser

# Ensure database directory exists and grant ownership to non-root user
RUN mkdir -p /app/database && \
    chown -R contactuser:contactuser /app

# Switch to non-root user
USER contactuser

# Expose application port
EXPOSE 5000

# Container healthcheck querying the /health endpoint
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Production command using Gunicorn WSGI server
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--access-logfile", "-", "--error-logfile", "-", "app:app"]
