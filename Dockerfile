# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production
ENV FLASK_DEBUG=0

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first (for better caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy ALL application code (including templates/ and static/)
COPY . .

# Create required directories for static file generation
RUN mkdir -p static/reports static/barcodes static/qrcodes static/logos static/uploads

# Expose port (Cloud Run expects 8080 by default)
EXPOSE 8080

# Use gunicorn with eventlet worker for SocketIO support
# Cloud Run injects $PORT (default 8080)
CMD exec gunicorn \
    --bind :${PORT:-8080} \
    --worker-class eventlet \
    --workers 1 \
    --threads 8 \
    --timeout 300 \
    --access-logfile - \
    --error-logfile - \
    wsgi:application
