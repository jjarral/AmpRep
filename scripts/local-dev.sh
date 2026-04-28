#!/bin/bash
# Ampoulex Local Development Script
# Usage: ./scripts/local-dev.sh [start|stop|logs|restart]

set -e

ACTION=${1:-start}

echo "======================================"
echo "Ampoulex Local Development"
echo "======================================"

case $ACTION in
    start)
        echo "🚀 Starting Ampoulex with Docker Compose..."
        if [ ! -f .env ]; then
            echo "⚠️  No .env file found. Creating from .env.example..."
            cp .env.example .env
            echo "✅ .env file created. Please update with your credentials."
        fi
        docker-compose up --build
        ;;
    stop)
        echo "🛑 Stopping Ampoulex..."
        docker-compose down
        ;;
    logs)
        echo "📋 Showing logs (Ctrl+C to exit)..."
        docker-compose logs -f web
        ;;
    restart)
        echo "🔄 Restarting Ampoulex..."
        docker-compose down
        docker-compose up -d --build
        ;;
    *)
        echo "Usage: $0 {start|stop|logs|restart}"
        echo ""
        echo "Commands:"
        echo "  start   - Start the application (default)"
        echo "  stop    - Stop the application"
        echo "  logs    - View application logs"
        echo "  restart - Restart the application"
        exit 1
        ;;
esac
