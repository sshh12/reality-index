#!/usr/bin/env python3
"""
Polymarket News Newsletter Generator

Analyzes Polymarket data to identify significant market shifts and generates 
AI-powered newsletters from the most interesting movements.

Usage:
    python main.py [command] [options]
"""

import argparse
import sys
import os
from market_analyzer.newsletter_generator import MarketNewsletterGenerator


def main():
    parser = argparse.ArgumentParser(
        description="Generate newsletters from Polymarket data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python main.py generate                    # Generate full newsletter
    python main.py summary                     # Quick market summary  
    python main.py search "election"           # Search for specific markets
    python main.py config                      # Show current settings
    
    # Custom thresholds
    python main.py generate --min-volume 50000 --min-change 10
    python main.py generate --hours 24 --max-markets 15
    
Environment Variables:
    OPENAI_API_KEY       - Required for AI newsletter generation
    POLYMARKET_SECRET_KEY - Optional, may be needed for some API calls
        """
    )
    
    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Generate command
    gen_parser = subparsers.add_parser('generate', help='Generate full newsletter')
    gen_parser.add_argument('--output', '-o', type=str, help='Output filename')
    gen_parser.add_argument('--min-volume', type=float, default=10000, 
                           help='Minimum market volume (default: 10000)')
    gen_parser.add_argument('--min-change', type=float, default=3.0,
                           help='Minimum price change %% (default: 3.0)')
    gen_parser.add_argument('--max-markets', type=int, default=10,
                           help='Maximum markets to include (default: 10)')
    gen_parser.add_argument('--hours', type=int, default=24,
                           help='Hours of history to analyze (default: 24)')
    gen_parser.add_argument('--limit', type=int, 
                           help='Limit number of markets to fetch for testing')
    
    # Summary command  
    sum_parser = subparsers.add_parser('summary', help='Show quick market summary')
    sum_parser.add_argument('--min-volume', type=float, default=10000,
                           help='Minimum market volume (default: 10000)')
    sum_parser.add_argument('--min-change', type=float, default=3.0,
                           help='Minimum price change %% (default: 3.0)')
    sum_parser.add_argument('--hours', type=int, default=24,
                           help='Hours of history to analyze (default: 24)')
    sum_parser.add_argument('--limit', type=int,
                           help='Limit number of markets to fetch for testing')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search and analyze specific markets')
    search_parser.add_argument('term', type=str, help='Search term for market questions')
    search_parser.add_argument('--hours', type=int, default=24,
                              help='Hours of history to analyze (default: 24)')
    
    # Config command
    config_parser = subparsers.add_parser('config', help='Show current configuration')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Check if command provided
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    # Check API key for AI commands
    if args.command in ['generate'] and not os.getenv('OPENAI_API_KEY'):
        print("❌ Error: OPENAI_API_KEY environment variable not set")
        print("   Please run: source env.sh")
        sys.exit(1)
    
    try:
        # Execute commands
        if args.command == 'generate':
            generator = MarketNewsletterGenerator(
                min_volume=args.min_volume,
                min_change_pct=args.min_change,
                max_markets=args.max_markets,
                hours_back=args.hours,
                market_limit=args.limit
            )
            
            print(f"🚀 Generating newsletter with settings:")
            print(f"   Min volume: ${args.min_volume:,.0f}")
            print(f"   Min change: {args.min_change}%")
            print(f"   Max markets: {args.max_markets}")
            print(f"   Time window: {args.hours} hours")
            print()
            
            output_path = generator.generate_newsletter(args.output)
            
            if output_path:
                print(f"🎉 Newsletter generated successfully!")
                print(f"📁 Location: {output_path}")
            
        elif args.command == 'summary':
            generator = MarketNewsletterGenerator(
                min_volume=args.min_volume,
                min_change_pct=args.min_change,
                hours_back=args.hours,
                market_limit=args.limit
            )
            generator.print_summary()
            
        elif args.command == 'search':
            generator = MarketNewsletterGenerator(hours_back=args.hours)
            generator.analyze_specific_market(args.term)
            
        elif args.command == 'config':
            generator = MarketNewsletterGenerator()
            config = generator.get_config_summary()
            
            print("⚙️  CURRENT CONFIGURATION")
            print("═" * 30)
            print(f"Min Volume: ${config['min_volume']:,.0f}")
            print(f"Min Change: {config['min_change_pct']}%")
            print(f"Max Markets: {config['max_markets']}")
            print(f"Time Window: {config['hours_back']} hours")
            print(f"Output Dir: {config['output_dir']}")
            print()
            print("Environment:")
            print(f"OpenAI API: {'✅ Set' if os.getenv('OPENAI_API_KEY') else '❌ Missing'}")
            print(f"Polymarket Key: {'✅ Set' if os.getenv('POLYMARKET_SECRET_KEY') else '❌ Missing'}")
            
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