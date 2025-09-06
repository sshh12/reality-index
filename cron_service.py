#!/usr/bin/env python3
"""
Railway-compatible cron service for Polymarket Newsletter
Runs the newsletter generation every Friday at 6 PM PST
"""

import os
import time
import schedule
import logging
from datetime import datetime
from market_analyzer.subscription_newsletter_generator import SubscriptionNewsletterGenerator

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/newsletter.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def validate_environment():
    """Validate required environment variables"""
    required_vars = ['OPENAI_API_KEY', 'POSTMARK_API_KEY', 'DATABASE_URL']
    
    for var in required_vars:
        if not os.getenv(var):
            logger.error(f"❌ Missing required environment variable: {var}")
            return False
    
    logger.info("✅ All required environment variables are set")
    return True

def send_newsletter():
    """Generate and send subscription-based newsletters"""
    try:
        logger.info("🚀 Starting subscription-based newsletter generation...")
        
        # Create subscription newsletter generator with weekly parameters
        generator = SubscriptionNewsletterGenerator(
            min_volume=10000,      # Default volume threshold
            min_change_pct=2.0,    # Lower threshold for weekly newsletters
            max_markets=10000,     # Allow all markets
            hours_back=168,        # 7 days (168 hours)
        )
        
        # Generate and send newsletters for all subscription combinations
        results = generator.generate_and_send_all_newsletters()
        
        if "error" in results:
            logger.error(f"❌ Newsletter generation failed: {results['error']}")
            return False
        
        logger.info(f"✅ Newsletter generation complete!")
        logger.info(f"   📰 Topic combinations processed: {results['total_combinations']}")
        logger.info(f"   📧 Total emails sent: {results['total_emails_sent']}")
        
        # Log details for each combination
        for result in results['results']:
            if 'error' in result:
                logger.error(f"   ❌ {result['topics']}: {result['error']}")
            else:
                logger.info(f"   ✅ {result['topics']}: {result['subscriber_count']} subscribers, {result['email_results']['successful_sends']} sent")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Newsletter generation failed: {str(e)}")
        return False

def send_test_email():
    """Send a test email to verify configuration"""
    try:
        logger.info("🧪 Sending startup test email...")
        
        # For now, skip test email as we're using subscription-based sending
        logger.info("✅ Skipping test email - using subscription-based system")
        return True
            
    except Exception as e:
        logger.error(f"❌ Test email failed: {str(e)}")
        return False

def main():
    """Main cron service loop"""
    logger.info("🌟 Starting Polymarket Newsletter Cron Service")
    
    # Validate environment
    if not validate_environment():
        logger.error("❌ Environment validation failed - exiting")
        exit(1)
    
    # Skip startup test email - service is ready
    
    # Schedule the subscription-based newsletter for every Friday at 6 PM PST
    schedule.every().friday.at("18:00").do(send_newsletter)
    
    logger.info("⏰ Subscription newsletter scheduled for every Friday at 6:00 PM PST")
    logger.info("🔄 Cron service running... (press Ctrl+C to stop)")
    
    # Keep the service running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("👋 Cron service stopped by user")
    except Exception as e:
        logger.error(f"💥 Cron service crashed: {str(e)}")
        exit(1)