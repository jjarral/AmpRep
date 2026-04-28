#!/bin/bash
# Ampoulex Deployment Script for Google Cloud Run
# Usage: ./scripts/deploy.sh [region] [project-id]

set -e

REGION=${1:-us-central1}
PROJECT_ID=${2:-ampoulex-bd71e}
IMAGE_NAME="ampoulex"
IMAGE_TAG="us-central1-docker.pkg.dev/${PROJECT_ID}/cloud-run-source-deploy/${IMAGE_NAME}:latest"

echo "======================================"
echo "Ampoulex Cloud Run Deployment Script"
echo "======================================"
echo "Region: ${REGION}"
echo "Project ID: ${PROJECT_ID}"
echo "Image: ${IMAGE_TAG}"
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI is not installed. Please install it first."
    echo "   https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install it first."
    echo "   https://docs.docker.com/get-docker/"
    exit 1
fi

# Get current project
CURRENT_PROJECT=$(gcloud config get-value project 2>/dev/null)
if [ "$CURRENT_PROJECT" != "$PROJECT_ID" ]; then
    echo "⚠️  Current project is '$CURRENT_PROJECT', not '$PROJECT_ID'"
    read -p "Do you want to switch to project '$PROJECT_ID'? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        gcloud config set project $PROJECT_ID
    fi
fi

# Enable required APIs
echo "📡 Enabling required APIs..."
gcloud services enable cloudbuild.googleapis.com run.googleapis.com artifactregistry.googleapis.com --quiet

# Build and submit
echo "🔨 Building Docker image with Cloud Build..."
gcloud builds submit --tag $IMAGE_TAG .

# Deploy to Cloud Run
echo "🚀 Deploying to Cloud Run..."
gcloud run deploy $IMAGE_NAME \
  --image $IMAGE_TAG \
  --platform managed \
  --region $REGION \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --timeout 300 \
  --min-instances 0 \
  --max-instances 10 \
  --set-env-vars="PORT=8080"

echo ""
echo "✅ Deployment complete!"
echo ""
echo "Service URL:"
gcloud run services describe $IMAGE_NAME --platform managed --region $REGION --format 'value(status.url)'
echo ""
echo "To view logs:"
echo "  gcloud run services logs read $IMAGE_NAME --region $REGION"
echo ""
echo "To update environment variables:"
echo "  gcloud run services update $IMAGE_NAME --set-env-vars=\"DATABASE_URL=your_url,SECRET_KEY=your_key\" --region $REGION"
