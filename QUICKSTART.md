# Ampoulex - Quick Start Guide

## 🚀 Deploy to Google Cloud Run (Recommended)

### One-Command Deployment

```bash
./scripts/deploy.sh us-central1 ampoulex-bd71e
```

This will:
1. Enable required Google Cloud APIs
2. Build the Docker image using Cloud Build
3. Deploy to Cloud Run with optimal settings
4. Provide you with the service URL

### Manual Deployment

```bash
# Build and submit
gcloud builds submit --tag us-central1-docker.pkg.dev/ampoulex-bd71e/cloud-run-source-deploy/ampoulex:latest .

# Deploy
gcloud run deploy ampoulex \
  --image us-central1-docker.pkg.dev/ampoulex-bd71e/cloud-run-source-deploy/ampoulex:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="DATABASE_URL=your_database_url,SECRET_KEY=your_secret_key"
```

## 💻 Local Development

### Using Docker Compose (Recommended)

```bash
# Start the application
./scripts/local-dev.sh start

# Or manually
cp .env.example .env
# Edit .env with your database credentials
docker-compose up --build
```

Access at: http://localhost:8080

### Default Credentials
- **Username**: admin
- **Password**: admin123

## 📋 Health Checks

After deployment, verify your application is running:

```bash
# Basic health check
curl https://your-service-url/ping

# Full health check (includes database)
curl https://your-service-url/health
```

## 🔧 Environment Variables

Required environment variables for production:

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | Flask secret key | `your-secret-key-here` |
| `DATABASE_URL` | PostgreSQL connection string | `postgres://user:pass@host/db?sslmode=require` |

Set them in Cloud Run:
```bash
gcloud run services update ampoulex \
  --set-env-vars="DATABASE_URL=your_url,SECRET_KEY=your_key" \
  --region us-central1
```

## 📊 Monitoring

View logs:
```bash
gcloud run services logs read ampoulex --region us-central1
```

Monitor in GCP Console:
- **Cloud Run** → **ampoulex** → **Logs**
- **Cloud Monitoring** → **Dashboards**

## ⚡ Performance Tips

For better performance in production:

```bash
# Increase memory
gcloud run services update ampoulex --memory=1Gi --region us-central1

# Reduce cold starts
gcloud run services update ampoulex --min-instances=1 --region us-central1

# Increase timeout for long operations
gcloud run services update ampoulex --timeout=600 --region us-central1
```

## 🛠️ Troubleshooting

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed troubleshooting guide.

---

**Need help?** Check the full [Deployment Guide](DEPLOYMENT.md).
