#!/usr/bin/env python3
"""
The Reality Index Newsletter Web Application

Usage:
    python main.py web [--port 8080] [--reload]
"""

import argparse
import sys
import os
from datetime import datetime


def main():
    parser = argparse.ArgumentParser(
        description="The Reality Index Newsletter Web Application",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python main.py web                         # Start web server on port 8080
    python main.py web --port 3000            # Start on custom port
    python main.py web --reload               # Start with auto-reload for development
    
    python main.py newsletter tech ai          # Generate newsletter for tech + AI topics
    python main.py newsletter crypto --dry-run # Generate crypto newsletter (no emails)
    python main.py newsletter sports --save-only # Save newsletter to file only
    
    python main.py test-newsletter tech ai     # Send test newsletter to shrivu1122@gmail.com
    
    python main.py list-newsletters            # List all archived newsletters
    python main.py list-newsletters --topics tech ai # List newsletters for specific topics
    python main.py delete-newsletter 123      # Delete newsletter with ID 123
        """
    )
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Web server command
    web_parser = subparsers.add_parser('web', help='Start the web server')
    web_parser.add_argument('--port', type=int, default=8080, help='Port to run the server on (default: 8080)')
    web_parser.add_argument('--reload', action='store_true', help='Enable auto-reload for development')
    
    # Manual newsletter trigger command
    newsletter_parser = subparsers.add_parser('newsletter', help='Manually trigger newsletter generation and sending')
    newsletter_parser.add_argument('topics', nargs='+', help='Topics to generate newsletter for (space-separated)')
    newsletter_parser.add_argument('--dry-run', action='store_true', help='Generate but do not send emails')
    newsletter_parser.add_argument('--save-only', action='store_true', help='Generate and save to file only, no emails or archiving')
    
    # Test newsletter command
    test_newsletter_parser = subparsers.add_parser('test-newsletter', help='Generate and send newsletter to test email')
    test_newsletter_parser.add_argument('topics', nargs='+', help='Topics to generate newsletter for (space-separated)')
    test_newsletter_parser.add_argument('--test-email', default='shrivu1122@gmail.com', help='Test email address (default: shrivu1122@gmail.com)')
    
    # List newsletters command
    list_parser = subparsers.add_parser('list-newsletters', help='List archived newsletters')
    list_parser.add_argument('--topics', nargs='*', help='Filter by topics (space-separated)')
    list_parser.add_argument('--limit', type=int, default=20, help='Maximum newsletters to show (default: 20)')
    
    # Delete newsletter command
    delete_parser = subparsers.add_parser('delete-newsletter', help='Delete archived newsletter by ID')
    delete_parser.add_argument('id', type=int, help='Newsletter ID to delete')
    delete_parser.add_argument('--confirm', action='store_true', help='Skip confirmation prompt')
    
    # Test prompt command
    prompt_parser = subparsers.add_parser('test-prompt', help='Generate and dump AI prompt to file for testing')
    prompt_parser.add_argument('topics', nargs='+', help='Topics to generate prompt for (space-separated)')
    prompt_parser.add_argument('--output', default='test_prompt.txt', help='Output file for prompt (default: test_prompt.txt)')
    
    # Sanity check command
    sanity_parser = subparsers.add_parser('sanity-check', help='Run sanity checks on price change calculations')
    sanity_parser.add_argument('--sample-size', type=int, default=50, help='Number of markets to analyze (default: 50)')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Check if command provided
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        if args.command == 'web':
            print("🌐 Starting The Reality Index web application...")
            print(f"   Port: {args.port}")
            print(f"   Reload: {'Enabled' if args.reload else 'Disabled'}")
            print()
            
            import uvicorn
            from backend.api import app
            
            uvicorn.run("backend.api:app", host="0.0.0.0", port=args.port, reload=args.reload)
            
        elif args.command == 'newsletter':
            from market_analyzer.subscription_newsletter_generator import SubscriptionNewsletterGenerator
            from market_analyzer.topic_config import get_topic_keys, get_display_name
            
            # Validate topics
            valid_topics = get_topic_keys()
            invalid_topics = [t for t in args.topics if t not in valid_topics]
            if invalid_topics:
                print(f"❌ Invalid topics: {invalid_topics}")
                print(f"   Valid topics: {valid_topics}")
                sys.exit(1)
            
            # Sort topics for consistency
            topics = sorted(args.topics)
            topic_names = [get_display_name(topic) for topic in topics]
            
            print(f"📰 Manual newsletter generation")
            print(f"   Topics: {' + '.join(topic_names)}")
            print(f"   Mode: {'Dry run (no emails)' if args.dry_run else 'Save only (no emails/archive)' if args.save_only else 'Full generation and sending'}")
            print()
            
            # Create generator (now hard-coded to 7 days)
            generator = SubscriptionNewsletterGenerator(
                min_volume=10000,
                min_change_pct=2.0,
                max_markets=10000
            )
            
            if args.save_only:
                # Generate and save to file only
                timestamp = datetime.now().strftime("%Y%m%d_%H%M")
                filename = f"manual_newsletter_{'_'.join(topics)}_{timestamp}.md"
                content = generator.generate_newsletter_for_topics(topics, filename)
                print(f"✅ Newsletter saved to newsletters/{filename}")
                
            else:
                # Create a fake subscriber list or get real ones
                if args.dry_run:
                    print("🧪 Dry run mode - generating content without sending emails...")
                    content = generator.generate_newsletter_for_topics(topics)
                    if content:
                        print("✅ Newsletter generated successfully!")
                        print(f"📝 Content preview: {len(content)} characters")
                    else:
                        print("❌ Failed to generate newsletter content")
                else:
                    # Get real subscribers for this topic combination
                    from backend.database.database import get_db_session
                    from backend.database.models import Subscription
                    
                    with get_db_session() as db:
                        subscribers = generator.get_subscribers_for_topics(topics)
                        
                    if not subscribers:
                        print(f"⚠️  No subscribers found for topics: {topic_names}")
                        print("   Newsletter will be generated but no emails will be sent")
                        content = generator.generate_newsletter_for_topics(topics)
                        if content:
                            print("✅ Newsletter generated successfully (no subscribers to email)")
                    else:
                        print(f"📧 Found {len(subscribers)} subscribers")
                        
                        # Generate newsletter content
                        newsletter_content = generator.generate_newsletter_for_topics(topics)
                        
                        if not newsletter_content:
                            print("❌ Failed to generate newsletter content")
                            sys.exit(1)
                        
                        # Send emails
                        from market_analyzer.subscription_email_sender import SubscriptionEmailSender
                        email_sender = SubscriptionEmailSender()
                        
                        email_results = email_sender.send_newsletter_to_subscribers(
                            newsletter_content, 
                            subscribers,
                            topics
                        )
                        
                        print(f"✅ Newsletter sent!")
                        print(f"   📧 Emails sent: {email_results['successful_sends']}")
                        print(f"   ❌ Failed sends: {email_results['failed_sends']}")
                        
                        # Archive the newsletter
                        if email_results["successful_sends"] > 0:
                            from backend.database.database import get_db_session
                            from backend.database.models import NewsletterArchive
                            
                            title = f"The Reality Index: {' + '.join(topic_names)} Weekly Update"
                            html_content = email_sender.markdown_to_html(newsletter_content, "")
                            
                            with get_db_session() as db:
                                NewsletterArchive.create(
                                    db=db,
                                    topics=topics,
                                    title=title,
                                    content_html=html_content,
                                    content_markdown=newsletter_content,
                                    subscriber_count=email_results["successful_sends"]
                                )
                            
                            print("📁 Newsletter archived to database")
        
        elif args.command == 'test-newsletter':
            from market_analyzer.subscription_newsletter_generator import SubscriptionNewsletterGenerator
            from market_analyzer.subscription_email_sender import SubscriptionEmailSender
            from market_analyzer.topic_config import get_topic_keys, get_display_name
            from backend.database.database import get_db_session
            from backend.database.models import NewsletterArchive, Subscription
            
            # Validate topics
            valid_topics = get_topic_keys()
            invalid_topics = [t for t in args.topics if t not in valid_topics]
            if invalid_topics:
                print(f"❌ Invalid topics: {invalid_topics}")
                print(f"   Valid topics: {valid_topics}")
                sys.exit(1)
            
            # Sort topics for consistency
            topics = sorted(args.topics)
            topic_names = [get_display_name(topic) for topic in topics]
            
            print(f"🧪 Test newsletter generation and sending")
            print(f"   Topics: {' + '.join(topic_names)}")
            print(f"   Test email: {args.test_email}")
            print()
            
            # Create generator (now hard-coded to 7 days)
            generator = SubscriptionNewsletterGenerator(
                min_volume=10000,
                min_change_pct=2.0,
                max_markets=10000
            )
            
            # Generate newsletter content
            newsletter_content = generator.generate_newsletter_for_topics(topics)
            
            if not newsletter_content:
                print("❌ Failed to generate newsletter content")
                sys.exit(1)
            
            print("✅ Newsletter content generated successfully")
            
            # Create a fake subscriber for the test email
            class TestSubscriber:
                def __init__(self, email, topics, token):
                    self.email = email
                    self.topics = topics
                    self.unsubscribe_token = token
            
            test_subscriber = TestSubscriber(args.test_email, topics, "test-token-123")
            
            # Send email
            email_sender = SubscriptionEmailSender()
            email_results = email_sender.send_newsletter_to_subscribers(
                newsletter_content,
                [test_subscriber],
                topics
            )
            
            print(f"📧 Email results:")
            print(f"   ✅ Successful: {email_results['successful_sends']}")
            print(f"   ❌ Failed: {email_results['failed_sends']}")
            
            if email_results['failed_sends'] > 0:
                for result in email_results['results']:
                    if result['status'] == 'failed':
                        print(f"   Error: {result['error']}")
            
            # Save to archive
            if email_results["successful_sends"] > 0:
                title = f"The Reality Index: {' + '.join(topic_names)} Weekly Update"
                html_content = email_sender.markdown_to_html(newsletter_content, "")
                
                with get_db_session() as db:
                    NewsletterArchive.create(
                        db=db,
                        topics=topics,
                        title=title,
                        content_html=html_content,
                        content_markdown=newsletter_content,
                        subscriber_count=1  # Test email count
                    )
                
                print("📁 Newsletter archived to database")
                print(f"✅ Test complete! Newsletter sent to {args.test_email} and archived")
            else:
                print("❌ Test failed - newsletter not sent or archived")
        
        elif args.command == 'list-newsletters':
            from backend.database.database import get_db_session
            from backend.database.models import NewsletterArchive
            from market_analyzer.topic_config import get_display_name
            
            print("📰 Archived Newsletters")
            print("═" * 50)
            
            with get_db_session() as db:
                if args.topics:
                    # Filter by specific topics
                    newsletters = NewsletterArchive.get_by_topics(db, sorted(args.topics), args.limit)
                    topic_names = [get_display_name(topic) for topic in sorted(args.topics)]
                    print(f"Showing newsletters for: {' + '.join(topic_names)}")
                else:
                    # Show all newsletters
                    newsletters = NewsletterArchive.get_all_recent(db, args.limit)
                    print("Showing all newsletters")
                
                print(f"Found {len(newsletters)} newsletters:")
                print()
                
                if not newsletters:
                    print("No newsletters found.")
                else:
                    for newsletter in newsletters:
                        topic_names = [get_display_name(topic) for topic in newsletter.topics]
                        print(f"ID: {newsletter.id}")
                        print(f"Title: {newsletter.title}")
                        print(f"Topics: {' + '.join(topic_names)}")
                        print(f"Sent: {newsletter.sent_at.strftime('%Y-%m-%d %H:%M:%S')}")
                        print(f"Subscribers: {newsletter.subscriber_count}")
                        print("-" * 40)
        
        elif args.command == 'delete-newsletter':
            from backend.database.database import get_db_session
            from backend.database.models import NewsletterArchive
            
            with get_db_session() as db:
                newsletter = db.query(NewsletterArchive).filter(NewsletterArchive.id == args.id).first()
                
                if not newsletter:
                    print(f"❌ Newsletter with ID {args.id} not found")
                    sys.exit(1)
                
                print(f"📰 Newsletter to delete:")
                print(f"   ID: {newsletter.id}")
                print(f"   Title: {newsletter.title}")
                print(f"   Topics: {newsletter.topics}")
                print(f"   Sent: {newsletter.sent_at}")
                print(f"   Subscribers: {newsletter.subscriber_count}")
                print()
                
                if args.confirm:
                    # Skip confirmation prompt
                    db.delete(newsletter)
                    db.commit()
                    print(f"✅ Newsletter {args.id} deleted successfully")
                else:
                    print("❌ Interactive confirmation not supported in this environment.")
                    print(f"   Use --confirm flag to delete: python main.py delete-newsletter {args.id} --confirm")
        
        elif args.command == 'test-prompt':
            from market_analyzer.subscription_newsletter_generator import SubscriptionNewsletterGenerator
            from market_analyzer.topic_config import get_topic_keys, get_display_name, get_prompt_context_for_topics
            from market_analyzer.openai_client import NewsletterAI
            
            # Validate topics
            valid_topics = get_topic_keys()
            invalid_topics = [t for t in args.topics if t not in valid_topics]
            if invalid_topics:
                print(f"❌ Invalid topics: {invalid_topics}")
                print(f"   Valid topics: {valid_topics}")
                sys.exit(1)
            
            # Sort topics for consistency
            topics = sorted(args.topics)
            topic_names = [get_display_name(topic) for topic in topics]
            
            print(f"🔍 Generating AI prompt for topics: {' + '.join(topic_names)}")
            print(f"📁 Output file: {args.output}")
            print()
            
            # Create generator to get the data (now hard-coded to 7 days)
            generator = SubscriptionNewsletterGenerator(
                min_volume=10000,
                min_change_pct=2.0,
                max_markets=10000
            )
            
            # Get market data (same as newsletter generation)
            all_markets = generator.polymarket.get_all_markets()
            print(f"   Found {len(all_markets)} total markets")
            
            active_markets = generator.polymarket.filter_active_markets(all_markets, generator.processor.min_volume)
            print(f"   {len(active_markets)} active markets meet criteria")
            
            if not active_markets:
                print("❌ No markets meet the criteria.")
                sys.exit(1)
            
            markets_with_changes = generator.polymarket.calculate_price_changes(active_markets)
            print(f"   {len(markets_with_changes)} markets have price data")
            
            if not markets_with_changes:
                print("❌ No markets have sufficient price history.")
                sys.exit(1)
            
            # Process data for newsletter
            newsletter_data = generator.processor.create_newsletter_data(markets_with_changes, generator.hours_back)
            
            # Get topic context
            topic_context = get_prompt_context_for_topics(topics)
            
            # Create AI client and build prompt (without calling OpenAI)
            ai = NewsletterAI()
            
            # Build the prompt
            base_prompt = ai._build_newsletter_prompt(newsletter_data, "tech-outlook")
            
            if topic_context:
                context_addition = f"""

SUBSCRIBER TOPIC FOCUS: {topic_context}

Please emphasize insights and analysis that align with these topic areas while maintaining comprehensive coverage of all significant market movements."""
                full_prompt = base_prompt + context_addition
            else:
                full_prompt = base_prompt
            
            # Get enhanced instructions
            from market_analyzer.newsletter_formats import DEVELOPER_INSTRUCTIONS
            enhanced_instructions = f"""{DEVELOPER_INSTRUCTIONS}

TOPIC FOCUS: {topic_context}

When analyzing the market data, prioritize insights that align with the subscriber's topic interests while maintaining comprehensive coverage of all significant market movements."""
            
            # Write to file
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write("# AI NEWSLETTER GENERATION PROMPT TEST\n\n")
                f.write(f"## Configuration\n")
                f.write(f"- Topics: {', '.join(topic_names)}\n")
                f.write(f"- Hours analyzed: {generator.hours_back} (7 days)\n")
                f.write(f"- Markets analyzed: {len(markets_with_changes)}\n")
                f.write(f"- Min volume: ${generator.processor.min_volume:,}\n")
                f.write(f"- Min change: {generator.processor.min_change_pct}%\n\n")
                
                f.write("## DEVELOPER INSTRUCTIONS\n\n")
                f.write(enhanced_instructions)
                f.write("\n\n" + "="*80 + "\n\n")
                
                f.write("## USER PROMPT\n\n")
                f.write(full_prompt)
            
            print(f"✅ AI prompt saved to: {args.output}")
            print(f"📊 Contains data from {len(markets_with_changes)} markets over {generator.hours_back} hours")
            print(f"🎯 Topic context: {topic_context[:100]}..." if len(topic_context) > 100 else f"🎯 Topic context: {topic_context}")
        
        elif args.command == 'sanity-check':
            from market_analyzer.subscription_newsletter_generator import SubscriptionNewsletterGenerator
            
            print(f"🔍 Running price change sanity check...")
            print(f"📊 Sample size: {args.sample_size} markets")
            print()
            
            # Create generator (now hard-coded to 7 days)
            generator = SubscriptionNewsletterGenerator(
                min_volume=5000,  # Lower threshold to get more markets
                min_change_pct=1.0,  # Lower threshold
                max_markets=10000
            )
            
            # Get market data
            all_markets = generator.polymarket.get_all_markets(limit=1000)
            print(f"   📈 Fetched {len(all_markets)} markets from API")
            
            active_markets = generator.polymarket.filter_active_markets(all_markets, 1000)  # Lower volume filter
            print(f"   ✅ {len(active_markets)} active markets meet criteria")
            
            if not active_markets:
                print("❌ No markets available for analysis")
                sys.exit(1)
            
            # Analyze the first N markets
            sample_markets = active_markets[:args.sample_size]
            print(f"   🔬 Analyzing sample of {len(sample_markets)} markets")
            print()
            
            # Check what price change data is available
            one_day_count = 0
            one_week_count = 0
            one_month_count = 0
            no_data_count = 0
            
            price_period_analysis = []
            
            for i, market in enumerate(sample_markets):
                market_analysis = {
                    "question": market.get("question", "Unknown")[:60] + "...",
                    "volume": market.get("volume", 0),
                    "has_1day": bool(market.get("oneDayPriceChange")),
                    "has_1week": bool(market.get("oneWeekPriceChange")), 
                    "has_1month": bool(market.get("oneMonthPriceChange")),
                    "1day_change": market.get("oneDayPriceChange", 0),
                    "1week_change": market.get("oneWeekPriceChange", 0),
                    "1month_change": market.get("oneMonthPriceChange", 0)
                }
                
                # Determine which period would be used (NEW priority: 1week -> 1day -> 1month)
                if market.get("oneWeekPriceChange"):
                    one_week_count += 1
                    market_analysis["used_period"] = "1week"
                elif market.get("oneDayPriceChange"):
                    one_day_count += 1
                    market_analysis["used_period"] = "1day"
                elif market.get("oneMonthPriceChange"):
                    one_month_count += 1
                    market_analysis["used_period"] = "1month"
                else:
                    no_data_count += 1
                    market_analysis["used_period"] = "none"
                    
                price_period_analysis.append(market_analysis)
            
            print("📊 PRICE CHANGE PERIOD ANALYSIS")
            print("="*50)
            print(f"Using 1-day changes:   {one_day_count:3d} markets ({one_day_count/len(sample_markets)*100:.1f}%)")
            print(f"Using 1-week changes:  {one_week_count:3d} markets ({one_week_count/len(sample_markets)*100:.1f}%)")
            print(f"Using 1-month changes: {one_month_count:3d} markets ({one_month_count/len(sample_markets)*100:.1f}%)")
            print(f"No price data:         {no_data_count:3d} markets ({no_data_count/len(sample_markets)*100:.1f}%)")
            print()
            
            if one_week_count > one_day_count:
                print("✅ GOOD: More markets are using 1-week changes than 1-day!")
                print("   This is appropriate for 7-day (168 hour) weekly analysis.")
                print()
            elif one_day_count > one_week_count:
                print("⚠️  WARNING: More markets are using 1-day price changes than 1-week!")
                print("   This means most 'weekly' analysis is actually daily movements.")
                print()
            
            # Show detailed breakdown for first 10 markets
            print("📋 DETAILED SAMPLE (First 10 markets):")
            print("-" * 90)
            print(f"{'Question':<45} {'Period':<8} {'1D':<8} {'1W':<8} {'1M':<8}")
            print("-" * 90)
            
            for i, analysis in enumerate(price_period_analysis[:10]):
                question = analysis["question"][:44]
                period = analysis["used_period"]
                day_change = f"{analysis['1day_change']:+.3f}" if analysis['has_1day'] else "N/A"
                week_change = f"{analysis['1week_change']:+.3f}" if analysis['has_1week'] else "N/A"  
                month_change = f"{analysis['1month_change']:+.3f}" if analysis['has_1month'] else "N/A"
                
                print(f"{question:<45} {period:<8} {day_change:<8} {week_change:<8} {month_change:<8}")
            
            print()
            
            # Recommendation
            if one_day_count > len(sample_markets) * 0.7:
                print("🚨 CRITICAL ISSUE DETECTED!")
                print("   70%+ of markets are using 1-day price changes instead of 1-week.")
                print("   For a weekly newsletter analyzing 168 hours, we should prioritize")
                print("   1-week changes over 1-day changes.")
                print()
                print("💡 RECOMMENDATION:")
                print("   Modify calculate_price_changes() to prioritize:")
                print("   1. oneWeekPriceChange (for 7-day analysis)")  
                print("   2. oneDayPriceChange (as fallback)")
                print("   3. oneMonthPriceChange (as last resort)")
            else:
                print("✅ Price change periods look reasonable for weekly analysis.")
            
    except KeyboardInterrupt:
        print("\n👋 Operation cancelled by user")
        sys.exit(0)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if "--debug" in sys.argv:
            raise
        sys.exit(1)


if __name__ == "__main__":
    main()