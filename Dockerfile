FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    cron \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create newsletters directory
RUN mkdir -p newsletters

# Set timezone to PST/PDT
ENV TZ=America/Los_Angeles

# Copy entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Expose port (required by Railway even for cron jobs)
EXPOSE 8080

# Use entrypoint script
ENTRYPOINT ["/entrypoint.sh"]