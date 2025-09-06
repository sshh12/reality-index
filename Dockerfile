# Multi-stage build: Node.js for frontend, Python for backend
FROM node:18-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy frontend package files
COPY frontend/package.json frontend/package*.json ./

# Install frontend dependencies
RUN npm install

# Copy frontend source
COPY frontend/ ./

# Build frontend
RUN npm run build

# Python stage for backend and final image
FROM python:3.12-slim

WORKDIR /app

# Install system dependencies including nginx
RUN apt-get update && apt-get install -y \
    cron \
    curl \
    nginx \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Copy built frontend from the previous stage
COPY --from=frontend-builder /app/static ./static

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Create necessary directories
RUN mkdir -p newsletters static

# Make database init script executable
RUN chmod +x backend/database/init.py

# Set timezone to PST/PDT
ENV TZ=America/Los_Angeles

# Copy and set up entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose port
EXPOSE 8080

# Use entrypoint script
ENTRYPOINT ["/entrypoint.sh"]