#!/bin/bash

# Automated Docker build and local deployment

set -e

# Display progress message
echo "Starting Docker build and deployment..."

# Build the Docker image
echo "Building Docker image..."
docker build -t myapp .

# Check if the build was successful
if [ $? -ne 0 ]; then
    echo "Error: Docker build failed."
    exit 1
fi

echo "Docker image built successfully."

# Run the Docker container
echo "Running Docker container..."
docker run --rm -d -p 8080:8080 myapp

# Check if the container started successfully
if [ $? -ne 0 ]; then
    echo "Error: Failed to start Docker container."
    exit 1
fi

echo "Docker container is running."

# Display the status of the running container
docker ps | grep myapp

echo "Deployment completed successfully!"