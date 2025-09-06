# The Reality Index Newsletter

An AI-powered subscription newsletter service that analyzes prediction market data to deliver insights on what will actually happen across politics, tech, crypto, sports, economics, and culture.

<img width="902" height="650" alt="Screenshot 2025-08-10 at 5 06 33 PM" src="https://github.com/user-attachments/assets/7c1d3361-8dce-483a-a913-078f3aa0881e" />


## What This Does

A full-stack web application with subscription management that delivers personalized prediction market insights:

- **React subscription interface** where users choose from 8 topic categories
- **Database-backed user management** with topic-based segmentation
- **AI-generated newsletters** that analyze thousands of prediction markets
- **Automated weekly delivery** every Friday at 6 PM PST
- **Newsletter archive** with preview functionality

## Quick Start

### Prerequisites
- Python 3.12+
- PostgreSQL database
- OpenAI API key (for newsletter generation)
- Postmark API key (for email delivery)

### Development Setup

1. **Clone and install:**
   ```bash
   git clone <your-repo>
   cd prediction-market-news
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   Create an `env.sh` file with your API keys:
   ```bash
   export OPENAI_API_KEY="your-openai-key"
   export POSTMARK_API_KEY="your-postmark-key"  
   export DATABASE_URL="postgresql://user:pass@host:port/dbname"
   export BASE_URL="https://your-domain.com"
   ```

3. **Start development servers:**
   ```bash
   source env.sh
   ./dev.sh  # Starts both React frontend and FastAPI backend
   ```

### Usage

```bash
# Start web application
python main.py web --reload

# Generate test newsletter
python main.py test-newsletter tech ai

# List archived newsletters
python main.py list-newsletters

# Delete newsletter by ID
python main.py delete-newsletter 123 --confirm
```

## Deployment

Deploy to Railway as a single full-stack service:

1. **Environment variables:**
   - `OPENAI_API_KEY`
   - `POSTMARK_API_KEY` 
   - `DATABASE_URL`
   - `BASE_URL`

2. **Single container** runs both web app and cron scheduler

3. **Automated newsletters** sent every Friday at 6 PM PST to all subscribers

