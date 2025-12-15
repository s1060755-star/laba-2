#!/bin/bash

# Production Deployment Script for Laba-2 Flask Application
# Usage: ./deploy.sh [build|start|stop|restart|logs|backup|status]

set -e

PROJECT_NAME="laba-2-main"
BACKUP_DIR="./backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Helper functions
info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if .env file exists
check_env() {
    if [ ! -f .env ]; then
        warning ".env file not found!"
        if [ -f .env.production ]; then
            info "Copying .env.production to .env..."
            cp .env.production .env
            warning "Please edit .env and set FLASK_SECRET to a secure random value!"
            exit 1
        else
            error "No .env.production template found!"
            exit 1
        fi
    fi
    
    # Check if FLASK_SECRET is set to default value
    if grep -q "CHANGE_ME_TO_SECURE_RANDOM_STRING" .env; then
        error "FLASK_SECRET is not set to a secure value in .env!"
        info "Generate a secure key with: python -c \"import secrets; print(secrets.token_hex(32))\""
        exit 1
    fi
}

# Build Docker image
build() {
    info "Building Docker image..."
    docker-compose build
    info "Build completed successfully!"
}

# Start application
start() {
    info "Starting application..."
    check_env
    docker-compose up -d
    info "Application started!"
    info "Waiting for health check..."
    sleep 5
    check_health
}

# Stop application
stop() {
    info "Stopping application..."
    docker-compose stop
    info "Application stopped!"
}

# Restart application
restart() {
    info "Restarting application..."
    check_env
    docker-compose restart
    info "Application restarted!"
    sleep 5
    check_health
}

# View logs
logs() {
    info "Showing logs (Ctrl+C to exit)..."
    docker-compose logs -f web
}

# Check application health
check_health() {
    info "Checking application health..."
    HEALTH_URL="http://localhost:5000/health"
    
    RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $HEALTH_URL || echo "000")
    
    if [ "$RESPONSE" = "200" ]; then
        info "✓ Health check passed!"
        info "Application is running at: http://localhost:5000"
    else
        error "✗ Health check failed! (HTTP $RESPONSE)"
        warning "Check logs with: ./deploy.sh logs"
        exit 1
    fi
}

# Show application status
status() {
    info "Application status:"
    docker-compose ps
    echo ""
    check_health
}

# Create database backup
backup() {
    info "Creating database backup..."
    
    mkdir -p $BACKUP_DIR
    
    CONTAINER_ID=$(docker-compose ps -q web)
    
    if [ -z "$CONTAINER_ID" ]; then
        error "Container is not running!"
        exit 1
    fi
    
    BACKUP_FILE="$BACKUP_DIR/backup_$TIMESTAMP.db"
    docker cp $CONTAINER_ID:/data/my_database.db $BACKUP_FILE
    
    if [ -f "$BACKUP_FILE" ]; then
        info "✓ Backup created: $BACKUP_FILE"
        info "Backup size: $(du -h $BACKUP_FILE | cut -f1)"
    else
        error "✗ Backup failed!"
        exit 1
    fi
}

# Deploy (full deployment process)
deploy() {
    info "Starting full deployment process..."
    
    check_env
    
    info "Step 1: Creating backup..."
    if docker-compose ps | grep -q "Up"; then
        backup || warning "Backup failed, continuing anyway..."
    else
        warning "Application not running, skipping backup..."
    fi
    
    info "Step 2: Building new image..."
    build
    
    info "Step 3: Stopping old containers..."
    docker-compose down
    
    info "Step 4: Starting new containers..."
    docker-compose up -d
    
    info "Step 5: Waiting for application to start..."
    sleep 10
    
    info "Step 6: Running health check..."
    check_health
    
    info "✓ Deployment completed successfully!"
    info "View logs with: ./deploy.sh logs"
}

# Show usage
usage() {
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  build     - Build Docker image"
    echo "  start     - Start application"
    echo "  stop      - Stop application"
    echo "  restart   - Restart application"
    echo "  logs      - View application logs"
    echo "  status    - Show application status"
    echo "  backup    - Create database backup"
    echo "  deploy    - Full deployment (backup, build, restart)"
    echo "  help      - Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 deploy    # Full deployment process"
    echo "  $0 logs      # View logs"
    echo "  $0 backup    # Create database backup"
}

# Main script logic
case "${1:-help}" in
    build)
        build
        ;;
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    logs)
        logs
        ;;
    status)
        status
        ;;
    backup)
        backup
        ;;
    deploy)
        deploy
        ;;
    help|--help|-h)
        usage
        ;;
    *)
        error "Unknown command: $1"
        usage
        exit 1
        ;;
esac
