# Deployment Guide for Ampoulex

This document provides comprehensive instructions for deploying the Ampoulex project on Google Cloud Platform's Cloud Run service, using Docker, and running the application locally with Docker Compose. It also includes information on environment variables, health checks, monitoring setup, and troubleshooting tips.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Cloud Run Deployment](#cloud-run-deployment)
3. [Docker Deployment](#docker-deployment)
4. [Local Development with Docker Compose](#local-development-with-docker-compose)
5. [Environment Variables Reference](#environment-variables-reference)
6. [Health Checks](#health-checks)
7. [Monitoring Setup](#monitoring-setup)
8. [Troubleshooting Tips](#troubleshooting-tips)

## Prerequisites

- **Google Cloud account** with billing enabled
- **Google Cloud SDK** installed and configured
- **Docker** installed for local development and container builds
- **Python 3.11+** for local development (optional)

### Install Google Cloud SDK

```bash
# Download and install from: https://cloud.google.com/sdk/docs/install
# Or use package manager:
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
gcloud init
```

### Enable Required APIs

```bash
gcloud services enable cloudbuild.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable artifactregistry.googleapis.com
```

## Cloud Run Deployment

### Option 1: Using Cloud Build (Recommended)

1. **Build and deploy using Cloud Build**:
   ```bash
   gcloud builds submit --tag us-central1-docker.pkg.dev/ampoulex-bd71e/cloud-run-source-deploy/ampoulex:latest
   ```

2. **Deploy to Cloud Run**:
   ```bash
   gcloud run deploy ampoulex \
     --image us-central1-docker.pkg.dev/ampoulex-bd71e/cloud-run-source-deploy/ampoulex:latest \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars="DATABASE_URL=your_database_url,SECRET_KEY=your_secret_key" \
     --memory 512Mi \
     --cpu 1 \
     --timeout 300 \
     --min-instances 0 \
     --max-instances 10
   ```

3. **Update environment variables** (if needed):
   ```bash
   gcloud run services update ampoulex \
     --set-env-vars="DATABASE_URL=your_new_database_url" \
     --region us-central1
   ```

### Option 2: Manual Docker Build and Push

1. **Build the Docker image locally**:
   ```bash
   docker build -t gcr.io/YOUR-PROJECT-ID/ampoulex .
   ```

2. **Push to Container Registry**:
   ```bash
   docker push gcr.io/YOUR-PROJECT-ID/ampoulex
   ```

3. **Deploy to Cloud Run**:
   ```bash
   gcloud run deploy ampoulex \
     --image gcr.io/YOUR-PROJECT-ID/ampoulex \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated
   ```

## Docker Deployment

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/jjarral/ampoulex.git
   cd ampoulex
   ```

2. **Build the Docker Image**:
   ```bash
   docker build -t ampoulex .
   ```

3. **Run the Docker Container**:
   ```bash
   docker run -p 8080:8080 \
     -e DATABASE_URL=postgres://user:password@localhost:5432/mydatabase \
     -e SECRET_KEY=your_secret_key \
     ampoulex
   ```
   
   Access the application at `http://localhost:8080`.

## Local Development with Docker Compose

1. **Create a `.env` file** (copy from `.env.example`):
   ```bash
   cp .env.example .env
   ```

2. **Update the `.env` file** with your database credentials and secret key.

3. **Start the Application**:
   ```bash
   docker-compose up
   ```
   
   The application will be accessible at `http://localhost:8080`.

4. **Run in detached mode**:
   ```bash
   docker-compose up -d
   ```

5. **View logs**:
   ```bash
   docker-compose logs -f web
   ```

6. **Stop the application**:
   ```bash
   docker-compose down
   ```

## Environment Variables Reference

| Variable Name | Description | Default | Required |
|---------------|-------------|---------|----------|
| `SECRET_KEY` | Flask secret key for session management | `dev-key-change-in-production` | Yes |
| `DATABASE_URL` | PostgreSQL database connection string | None | Yes |
| `PORT` | Port for the application to listen on | `8080` | No (Cloud Run sets this) |
| `FLASK_ENV` | Flask environment (`development` or `production`) | `production` | No |
| `DEBUG` | Enable debug mode | `False` | No |
| `ALLOWED_HOSTS` | Comma-separated list of allowed hosts | `*` | No |

### Example DATABASE_URL formats:

- **PostgreSQL (local)**: `postgres://user:password@localhost:5432/mydatabase`
- **PostgreSQL (Cloud SQL)**: `postgres://user:password@/mydatabase?host=/cloudsql/project:region:instance`
- **Neon/Serverless**: `postgres://user:password@host.neon.tech/mydatabase?sslmode=require`

## Health Checks

The application provides two health check endpoints:

### `/ping` - Basic Health Check
Simple endpoint that returns immediately:
```json
{"status": "ok"}
```

### `/health` - Full Health Check
Checks database connectivity:
```json
{"status": "healthy", "database": "connected"}
```

Or on failure:
```json
{"status": "unhealthy", "error": "error message"}
```

### Cloud Run Configuration

Cloud Run automatically configures health checks based on the container's startup. For custom configuration:

```bash
gcloud run services update ampoulex \
  --startupProbeTcpSocketPort=8080 \
  --livenessHttpGetPath=/health \
  --readinessHttpGetPath=/health \
  --region us-central1
```

## Monitoring Setup

### Google Cloud Monitoring

1. **Enable Monitoring API**:
   ```bash
   gcloud services enable monitoring.googleapis.com
   ```

2. **View metrics in GCP Console**:
   - Navigate to **Cloud Monitoring** → **Dashboards**
   - Create custom dashboards for:
     - Request latency
     - Error rates
     - Instance count
     - Memory/CPU usage

3. **Set up alerts**:
   - Go to **Cloud Monitoring** → **Alerting**
   - Create alert policies for:
     - High error rate (>5%)
     - High latency (p95 > 2s)
     - Service unavailable

### Application Logs

View logs in Cloud Run:
```bash
gcloud run services logs read ampoulex --region us-central1 --limit 50
```

Or in GCP Console: **Cloud Run** → **ampoulex** → **Logs**

## Troubleshooting Tips

### Common Issues

#### 1. Container fails to start
- **Check logs**: `gcloud run services logs read ampoulex --region us-central1`
- **Verify DATABASE_URL**: Ensure it's correctly formatted and accessible
- **Check memory/CPU limits**: Increase if getting OOM errors

#### 2. Database connection errors
- **Verify network access**: Cloud SQL instance must allow connections from Cloud Run
- **Check SSL requirements**: Add `?sslmode=require` for Neon/serverless databases
- **Test connection locally**: Use the same DATABASE_URL in Docker

#### 3. Static files not loading
- **Verify directories exist**: The Dockerfile creates required static directories
- **Check file permissions**: Ensure files are readable by the container

#### 4. WebSocket/SocketIO issues
- **Verify eventlet worker**: Dockerfile uses `--worker-class eventlet`
- **Check CORS settings**: `cors_allowed_origins="*"` in app/__init__.py

### Debugging Locally

1. **Run with Docker Compose**:
   ```bash
   docker-compose up --build
   ```

2. **View container logs**:
   ```bash
   docker logs CONTAINER_ID
   ```

3. **Access container shell**:
   ```bash
   docker exec -it CONTAINER_ID /bin/bash
   ```

4. **Test health endpoints**:
   ```bash
   curl http://localhost:8080/ping
   curl http://localhost:8080/health
   ```

### Performance Optimization

- **Increase timeout** for long-running operations:
  ```bash
  gcloud run services update ampoulex --timeout=600 --region us-central1
  ```

- **Set minimum instances** for faster cold starts:
  ```bash
  gcloud run services update ampoulex --min-instances=1 --region us-central1
  ```

- **Increase memory** for better performance:
  ```bash
  gcloud run services update ampoulex --memory=1Gi --region us-central1
  ```

---

End of Deployment Guide.
