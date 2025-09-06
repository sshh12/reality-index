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

# No longer using supervisor - processes managed directly

# Display startup information
echo "🚀 Starting The Reality Index Newsletter Service"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌐 Web App:              http://localhost:8080"
echo "⏰ Newsletter Scheduler:  Every Friday at 6 PM PST"
echo "📊 Admin Stats:          http://localhost:8080/api/admin/stats"
echo "❤️  Health Check:        http://localhost:8080/health"
echo "📈 Analysis Period:      7 days (168 hours) - 1-week price changes only"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Start both processes directly without supervisor
echo "🌐 Starting web application in background..."
PYTHONPATH=/app python -m uvicorn backend.api:app --host 0.0.0.0 --port 8080 &
WEB_PID=$!

echo "⏰ Starting cron scheduler in background..."  
PYTHONPATH=/app python cron_service.py &
CRON_PID=$!

echo "✅ Both processes started:"
echo "   🌐 Web app (PID: $WEB_PID)"  
echo "   ⏰ Cron scheduler (PID: $CRON_PID)"

# Function to cleanup on exit
cleanup() {
    echo "🛑 Shutting down processes..."
    kill $WEB_PID $CRON_PID 2>/dev/null || true
    wait $WEB_PID $CRON_PID 2>/dev/null || true
    echo "👋 Shutdown complete"
    exit 0
}

# Setup signal handlers
trap cleanup SIGINT SIGTERM

# Wait for both processes (this keeps the container running)
wait