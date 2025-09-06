#!/bin/bash

# Set up environment
cd /app
export PYTHONPATH=/app

# Validate required environment variables
if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ Error: OPENAI_API_KEY environment variable not set"
    exit 1
fi

if [ -z "$POSTMARK_API_KEY" ]; then
    echo "❌ Error: POSTMARK_API_KEY environment variable not set"
    exit 1
fi

if [ -z "$DATABASE_URL" ]; then
    echo "❌ Error: DATABASE_URL environment variable not set"
    exit 1
fi

echo "✅ Environment variables validated"

# Initialize database
echo "🗄️  Initializing database..."
PYTHONPATH=/app python backend/database/init.py

# Create supervisor log directories
mkdir -p /var/log/supervisor

# Start both web app and cron scheduler with supervisor
echo "🚀 Starting both web application and cron scheduler..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌐 Web App:              http://localhost:8080"
echo "⏰ Newsletter Scheduler:  Every Friday at 6 PM PST"
echo "📊 Admin Stats:          http://localhost:8080/api/admin/stats"
echo "❤️  Health Check:        http://localhost:8080/health"
echo "📋 Supervisor Status:    supervisorctl status"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check if supervisor is available and start both processes
if python -c "import supervisor.supervisord" 2>/dev/null; then
    echo "🔧 Using supervisor to manage both processes"
    exec python -m supervisor.supervisord -c /app/supervisord.conf
else
    echo "⚠️  Supervisor not available, starting processes individually"
    echo "🌐 Starting web application in background..."
    PYTHONPATH=/app python -m uvicorn backend.api:app --host 0.0.0.0 --port 8080 &
    
    echo "⏰ Starting cron scheduler..."
    PYTHONPATH=/app python cron_service.py
fi