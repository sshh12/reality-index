import os
from datetime import datetime
from typing import Optional, List, Dict, Set
from collections import defaultdict

from .polymarket_client import PolymarketClient
from .data_processor import MarketDataProcessor
from .openai_client import NewsletterAI
from .subscription_email_sender import SubscriptionEmailSender
from .topic_config import get_display_name, get_prompt_context_for_topics

# Import database functionality
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database.database import get_db_session
from backend.database.models import Subscription, NewsletterArchive


class SubscriptionNewsletterGenerator:
    """Newsletter generator that works with database subscriptions and topic filtering"""
    
    def __init__(self, 
                 min_volume: float = 10000,
                 min_change_pct: float = 2.0,
                 max_markets: int = 10000,
                 hours_back: int = 168,  # Weekly by default
                 market_limit: Optional[int] = None):
        
        self.polymarket = PolymarketClient()
        self.processor = MarketDataProcessor(min_volume, min_change_pct, max_markets)
        self.ai = NewsletterAI()
        self.hours_back = hours_back
        self.market_limit = market_limit
        
        # Create output directory if it doesn't exist
        self.output_dir = "newsletters"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def get_unique_topic_combinations(self) -> List[List[str]]:
        """Get all unique topic combinations from active subscriptions"""
        with get_db_session() as db:
            subscriptions = Subscription.get_active_subscriptions(db)
            
        # Create set of unique topic combinations
        topic_combinations = set()
        for subscription in subscriptions:
            # Convert list to sorted tuple for hashability
            topic_combo = tuple(sorted(subscription.topics))
            topic_combinations.add(topic_combo)
        
        # Convert back to list of lists and sort for consistency
        unique_combinations = [list(combo) for combo in sorted(topic_combinations)]
        
        print(f"📊 Found {len(unique_combinations)} unique topic combinations:")
        for combo in unique_combinations:
            print(f"   • {combo}")
        
        return unique_combinations
    
    def get_subscribers_for_topics(self, topics: List[str]) -> List[Subscription]:
        """Get all subscribers for a specific topic combination"""
        with get_db_session() as db:
            # Get all active subscriptions
            all_subscriptions = Subscription.get_active_subscriptions(db)
            
        # Filter for subscriptions that match this exact topic combination
        matching_subscribers = []
        for subscription in all_subscriptions:
            if sorted(subscription.topics) == sorted(topics):
                matching_subscribers.append(subscription)
        
        return matching_subscribers
    
    def generate_newsletter_for_topics(self, topics: List[str], output_file: Optional[str] = None) -> str:
        """Generate newsletter content filtered for specific topics"""
        
        print(f"🔍 Generating newsletter for topics: {topics}")
        
        # Step 1: Get all markets
        all_markets = self.polymarket.get_all_markets(self.market_limit)
        print(f"   Found {len(all_markets)} total markets")
        
        # Step 2: Filter active markets
        active_markets = self.polymarket.filter_active_markets(all_markets, self.processor.min_volume)
        print(f"   {len(active_markets)} active markets meet criteria")
        
        if not active_markets:
            print("❌ No markets meet the criteria. Try lowering the volume threshold.")
            return ""
        
        # Step 3: Calculate price changes
        print("📊 Analyzing price movements...")
        markets_with_changes = self.polymarket.calculate_price_changes(active_markets)
        print(f"   {len(markets_with_changes)} markets have price data")
        
        if not markets_with_changes:
            print("❌ No markets have sufficient price history.")
            return ""
        
        # Step 4: Process data for newsletter (no topic filtering - use all markets)
        print(f"📊 Processing newsletter data for topics: {topics}")
        newsletter_data = self.processor.create_newsletter_data(markets_with_changes)
        
        # Step 5: Generate newsletter content with tech-outlook format and topic context
        print(f"✍️  Generating newsletter with AI (tech-outlook format)...")
        topic_context = get_prompt_context_for_topics(topics)
        print(f"🎯 Topic context: {topic_context}")
        
        # We'll pass this context through a modified AI call
        newsletter_content = self.ai.generate_newsletter_with_context(newsletter_data, "tech-outlook", topic_context, topics)
        
        # Step 7: Save to file (optional)
        if output_file:
            output_path = os.path.join(self.output_dir, output_file)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(newsletter_content)
            print(f"📁 Newsletter saved to: {output_path}")
            return output_path
        
        return newsletter_content
    
    
    def generate_and_send_all_newsletters(self) -> Dict:
        """Generate and send newsletters for all unique topic combinations"""
        
        print("🚀 Starting subscription-based newsletter generation...")
        
        # Get unique topic combinations
        topic_combinations = self.get_unique_topic_combinations()
        
        if not topic_combinations:
            print("❌ No active subscriptions found.")
            return {"error": "No active subscriptions"}
        
        results = {
            "total_combinations": len(topic_combinations),
            "newsletters_generated": 0,
            "total_emails_sent": 0,
            "results": []
        }
        
        # Initialize email sender
        email_sender = SubscriptionEmailSender()
        
        # Generate newsletter for each unique topic combination
        for topics in topic_combinations:
            try:
                print(f"\n📰 Processing topic combination: {topics}")
                
                # Generate newsletter content
                newsletter_content = self.generate_newsletter_for_topics(topics)
                
                if not newsletter_content:
                    print(f"⚠️  Failed to generate newsletter for topics: {topics}")
                    continue
                
                # Get subscribers for this topic combination
                subscribers = self.get_subscribers_for_topics(topics)
                print(f"📧 Found {len(subscribers)} subscribers for {topics}")
                
                if not subscribers:
                    print(f"⚠️  No subscribers for topics: {topics}")
                    continue
                
                # Send emails to subscribers
                email_results = email_sender.send_newsletter_to_subscribers(
                    newsletter_content, 
                    subscribers,
                    topics
                )
                
                # Save newsletter to archive if emails were sent successfully
                if email_results["successful_sends"] > 0:
                    try:
                        # Generate newsletter title from topics
                        topic_names = [get_display_name(topic) for topic in topics]
                        title = f"The Reality Index: {' + '.join(topic_names)} Weekly Update"
                        
                        # Convert markdown to HTML for archiving (no unsubscribe link for previews)
                        html_content = email_sender.markdown_to_html(newsletter_content, "#preview")
                        
                        # Save to newsletter archive
                        with get_db_session() as db:
                            NewsletterArchive.create(
                                db=db,
                                topics=topics,
                                title=title,
                                content_html=html_content,
                                content_markdown=newsletter_content,
                                subscriber_count=email_results["successful_sends"]
                            )
                        
                        print(f"📁 Newsletter archived for topics: {topics}")
                        
                    except Exception as archive_error:
                        print(f"⚠️  Failed to archive newsletter: {archive_error}")
                
                results["newsletters_generated"] += 1
                results["total_emails_sent"] += email_results["successful_sends"]
                results["results"].append({
                    "topics": topics,
                    "subscriber_count": len(subscribers),
                    "email_results": email_results
                })
                
                print(f"✅ Completed {topics}: {email_results['successful_sends']} emails sent")
                
            except Exception as e:
                print(f"❌ Error processing topics {topics}: {e}")
                results["results"].append({
                    "topics": topics,
                    "error": str(e)
                })
        
        print(f"\n🎉 Newsletter distribution complete!")
        print(f"   📰 Newsletters generated: {results['newsletters_generated']}")
        print(f"   📧 Total emails sent: {results['total_emails_sent']}")
        
        return results