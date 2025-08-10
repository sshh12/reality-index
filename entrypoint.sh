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

if [ -z "$TO_EMAILS" ]; then
    echo "❌ Error: TO_EMAILS environment variable not set"
    exit 1
fi

echo "✅ Environment variables validated"

# Validate configuration without sending test email
echo "✅ Configuration validated - service ready"

# Set up cron job for Friday 6 PM PST (1 AM UTC Saturday)
echo "⏰ Setting up cron job..."

# Create cron job entry
cat << 'EOF' > /tmp/newsletter_cron
# Polymarket Newsletter - Every Friday at 6 PM PST (1 AM UTC Saturday)
0 1 * * 6 cd /app && PYTHONPATH=/app python main.py email --hours 168 --format macro-outlook >> /var/log/newsletter.log 2>&1
EOF

# Install cron job
crontab /tmp/newsletter_cron

# Create log file
touch /var/log/newsletter.log
chmod 666 /var/log/newsletter.log

# Start cron service
echo "🚀 Starting cron service..."
cron

# Run a simple HTTP server to keep the container alive (Railway requirement)
echo "🌐 Starting health check server on port 8080..."
cat << 'EOF' > health_server.py
import http.server
import socketserver
import json
from datetime import datetime

class HealthHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            status = {
                "status": "healthy",
                "service": "polymarket-newsletter",
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "next_run": "Every Friday at 6 PM PST (1 AM UTC Saturday)"
            }
            
            self.wfile.write(json.dumps(status).encode())
        elif self.path == '/logs':
            self.send_response(200)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            
            try:
                with open('/var/log/newsletter.log', 'r') as f:
                    self.wfile.write(f.read().encode())
            except FileNotFoundError:
                self.wfile.write(b"No logs yet.")
        else:
            super().do_GET()

PORT = 8080
with socketserver.TCPServer(("", PORT), HealthHandler) as httpd:
    print(f"Health check server running on port {PORT}")
    httpd.serve_forever()
EOF

python health_server.py