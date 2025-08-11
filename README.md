# Polymarket Newsletter Generator

An automated system that analyzes prediction market data from Polymarket and generates AI-powered newsletters about significant market movements and global events.

<img width="902" height="650" alt="Screenshot 2025-08-10 at 5 06 33 PM" src="https://github.com/user-attachments/assets/7c1d3361-8dce-483a-a913-078f3aa0881e" />


## What This Does

This system monitors thousands of prediction markets covering politics, economics, technology, and world events. When significant price movements occur, it:

- **Analyzes market data** to identify trending themes and price changes
- **Generates intelligent newsletters** using AI that explains what's happening and why
- **Sends professional reports** via email with market insights and predictions
- **Runs automatically** on a schedule to deliver regular market updates

## Quick Start

### Prerequisites
- Python 3.12+
- OpenAI API key (for newsletter generation)
- Postmark API key (for email delivery)
- Email addresses to send newsletters to

### Setup

1. **Clone and install:**
   ```bash
   git clone <your-repo>
   cd prediction-market-news
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   Create an `env.sh` file with your API keys:
   ```bash
   export OPENAI_API_KEY="your-openai-key"
   export POSTMARK_API_KEY="your-postmark-key"  
   export TO_EMAILS="email1@example.com,email2@example.com"
   ```

3. **Test the setup:**
   ```bash
   source env.sh
   python main.py test-email
   ```

### Usage

```bash
# Generate a newsletter file
python main.py generate

# Generate and email newsletter  
python main.py email

# Quick market summary
python main.py summary

# Search specific markets
python main.py search "election"

# Check configuration
python main.py config
```

### Newsletter Options

```bash
# Different time windows
python main.py generate --hours 168  # Last week
python main.py generate --hours 24   # Last day

# Different thresholds
python main.py generate --min-volume 50000 --min-change 5

# Custom email subject
python main.py email --subject "Weekly Market Update"
```

## Automated Deployment

### Railway

For automated weekly newsletters, deploy to Railway:

1. **Set environment variables** in Railway dashboard:
   - `OPENAI_API_KEY`
   - `POSTMARK_API_KEY` 
   - `TO_EMAILS`

2. **Deploy** - the system includes automated cron scheduling

3. **Newsletters sent** every Friday at 6 PM PST automatically

The system runs as a background service and handles scheduling, error recovery, and logging automatically.

