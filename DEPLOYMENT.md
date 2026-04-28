# Deployment Guide for Ampoulex

This document provides comprehensive instructions for deploying the Ampoulex project on Google Cloud Platform's Cloud Run service, using Docker, and running the application locally with Docker Compose. It also includes information on environment variables, health checks, monitoring setup, and troubleshooting tips.

## Table of Contents
1. [Cloud Run Deployment](#cloud-run-deployment)
2. [Docker Deployment](#docker-deployment)
3. [Local Development with Docker Compose](#local-development-with-docker-compose)
4. [Environment Variables Reference](#environment-variables-reference)
5. [Health Checks](#health-checks)
6. [Monitoring Setup](#monitoring-setup)
7. [Troubleshooting Tips](#troubleshooting-tips)

## Cloud Run Deployment
1. **Prerequisites**:
   - Google Cloud account.
   - Install Google Cloud SDK.
   - Enable Cloud Run API in your GCP project.

2. **Build the Docker Image**:
   ```bash
   gcloud builds submit --tag gcr.io/YOUR-PROJECT-ID/ampoulex
   ```  
   Replace `YOUR-PROJECT-ID` with your actual GCP project ID.

3. **Deploy the Image to Cloud Run**:
   ```bash
   gcloud run deploy ampoulex --image gcr.io/YOUR-PROJECT-ID/ampoulex --platform managed --region YOUR_REGION
   ```
   Replace `YOUR_REGION` with the desired GCP region (e.g., us-central1).

4. **Allow unauthenticated invocations** (if required):
   ```bash
   gcloud run services add-iam-policy-binding ampoulex --member='allUsers' --role='roles/run.invoker'
   ```

5. **Access your deployed service**:
   - Follow the provided URL after deployment completion.

## Docker Deployment
1. **Install Docker**:
   - Ensure Docker is installed and running on your machine.

2. **Clone the Repository**:
   ```bash
   git clone https://github.com/jjarral/ampoulex.git
   cd ampoulex
   ```

3. **Build the Docker Image**:
   ```bash
   docker build -t ampoulex .
   ```

4. **Run the Docker Container**:
   ```bash
   docker run -p 8080:8080 ampoulex
   ```
   Access the application at `http://localhost:8080`.

## Local Development with Docker Compose
1. **Install Docker Compose**:
   - Ensure Docker Compose is installed.

2. **Clone the Repository**:
   ```bash
   git clone https://github.com/jjarral/ampoulex.git
   cd ampoulex
   ```

3. **Start the Application using Docker Compose**:
   ```bash
   docker-compose up
   ```
   The application will be accessible at `http://localhost:8080`.

## Environment Variables Reference
| Variable Name | Description |
|----------------|-------------|
| `ENV_VAR_1`   | Description for environment variable 1 |
| `ENV_VAR_2`   | Description for environment variable 2 |

(Note: Replace with actual environment variables for your application.)

## Health Checks
- Configure health checks in Cloud Run:
  - **Readiness check**: Ensure the application is ready to serve traffic.
  - **Liveness check**: Ensure the application is still running and responsive.

## Monitoring Setup
- Use Google Cloud’s operations suite (formerly Stackdriver) for monitoring:
  1. **Enable Monitoring API** in your GCP project.
  2. **View metrics** in the GCP Console under Cloud Monitoring.

## Troubleshooting Tips
- **Common Issues**:
   - Verify Docker is running if you encounter issues with Docker commands.
   - Ensure you have the correct permissions in GCP for deploying to Cloud Run.
   - Check the logs in GCP for detailed error information.
- **Debugging Locally**:
   - Use Docker logs to view output from your application:
   ```bash
   docker logs CONTAINER_ID
   ```
   Replace `CONTAINER_ID` with your actual container ID.

---

End of Deployment Guide.