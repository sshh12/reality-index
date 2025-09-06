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
            
            # Create generator
            generator = SubscriptionNewsletterGenerator(
                min_volume=10000,
                min_change_pct=2.0,
                max_markets=10000,
                hours_back=168,  # 7 days
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
            
            # Create generator
            generator = SubscriptionNewsletterGenerator(
                min_volume=10000,
                min_change_pct=2.0,
                max_markets=10000,
                hours_back=168,  # 7 days
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