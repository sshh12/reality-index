import os
from datetime import datetime
from typing import Optional
from .polymarket_client import PolymarketClient
from .data_processor import MarketDataProcessor
from .openai_client import NewsletterAI


class MarketNewsletterGenerator:
    def __init__(self, 
                 min_volume: float = 10000,
                 min_change_pct: float = 5.0,
                 max_markets: int = 10000,
                 hours_back: int = 24,
                 market_limit: Optional[int] = None,
                 format_type: str = "detailed-technical-letter"):
        
        self.polymarket = PolymarketClient()
        self.processor = MarketDataProcessor(min_volume, min_change_pct, max_markets)
        self.ai = NewsletterAI()
        self.hours_back = hours_back
        self.market_limit = market_limit
        self.format_type = format_type
        
        # Create output directory if it doesn't exist
        self.output_dir = "newsletters"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate_newsletter(self, output_file: Optional[str] = None) -> str:
        """Generate complete newsletter from Polymarket data"""
        
        print("🔍 Fetching Polymarket data...")
        
        # Step 1: Get all markets
        all_markets = self.polymarket.get_all_markets(self.market_limit)
        print(f"   Found {len(all_markets)} total markets{' (limited)' if self.market_limit else ''}")
        
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
            print("❌ No markets have sufficient price history. Try increasing the time window.")
            return ""
        
        # Step 4: Process data for newsletter
        newsletter_data = self.processor.create_newsletter_data(markets_with_changes)
        
        significant_moves = newsletter_data["summary_stats"]["significant_moves"]
        print(f"   {significant_moves} markets show significant movements")
        
        if significant_moves == 0:
            print("ℹ️  No significant market movements detected. Generating summary anyway...")
        
        # Step 5: Generate newsletter content
        print(f"✍️  Generating newsletter with AI ({self.format_type})...")
        newsletter_content = self.ai.generate_newsletter(newsletter_data, self.format_type)
        
        # Step 6: Save to file
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            output_file = f"polymarket_newsletter_{timestamp}.md"
        
        output_path = os.path.join(self.output_dir, output_file)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(newsletter_content)
        
        print(f"✅ Newsletter saved to: {output_path}")
        return output_path
    
    def print_summary(self) -> None:
        """Print a quick summary of market movements without generating full newsletter"""
        
        print("🔍 Fetching market summary...")
        
        # Get and process data
        all_markets = self.polymarket.get_all_markets(self.market_limit)
        active_markets = self.polymarket.filter_active_markets(all_markets, self.processor.min_volume)
        markets_with_changes = self.polymarket.calculate_price_changes(active_markets)
        
        # Process data
        newsletter_data = self.processor.create_newsletter_data(markets_with_changes)
        top_markets = newsletter_data["top_markets"]
        stats = newsletter_data["summary_stats"]
        
        # Print summary
        print(f"\n📈 POLYMARKET MOVEMENT SUMMARY")
        print(f"═" * 50)
        print(f"Markets Analyzed: {stats['total_markets_analyzed']}")
        print(f"Significant Moves: {stats['significant_moves']}")
        print(f"Average Change: {stats['avg_change_pct']}")
        print(f"Time Period: Last {self.hours_back} hours")
        print()
        
        if top_markets:
            print("🔥 TOP MOVEMENTS:")
            for i, market in enumerate(top_markets[:5], 1):
                direction = "📈" if market["raw_change"] > 0 else "📉"
                print(f"{i}. {direction} {market['question'][:60]}...")
                print(f"   {market['previous_price']} → {market['current_price']} ({market['change_pct']} change)")
                print(f"   Volume: {market['volume']} | {market['category']}")
                print()
        else:
            print("No significant movements detected.")
    
    def analyze_specific_market(self, search_term: str) -> None:
        """Analyze a specific market by searching for keywords"""
        
        print(f"🔍 Searching for markets containing: '{search_term}'...")
        
        all_markets = self.polymarket.get_all_markets()
        
        # Search for markets containing the term
        matching_markets = [
            market for market in all_markets 
            if search_term.lower() in market.get("question", "").lower()
        ]
        
        if not matching_markets:
            print(f"❌ No markets found containing '{search_term}'")
            return
        
        print(f"   Found {len(matching_markets)} matching markets")
        
        # Get price changes for matching markets
        markets_with_changes = self.polymarket.calculate_price_changes(matching_markets, self.hours_back)
        
        for market in markets_with_changes:
            formatted = self.processor.format_market_summary(market)
            
            print(f"\n📊 {formatted['question']}")
            print(f"   Category: {formatted['category']}")
            print(f"   Price: {formatted['previous_price']} → {formatted['current_price']} ({formatted['direction']} {formatted['change_pct']})")
            print(f"   Volume: {formatted['volume']}")
            print(f"   Closes: {formatted['end_date']}")
            
            # Get AI analysis
            analysis = self.ai.generate_market_analysis(formatted)
            print(f"\n   Analysis: {analysis}")
    
    def get_config_summary(self) -> dict:
        """Get current configuration settings"""
        return {
            "min_volume": self.processor.min_volume,
            "min_change_pct": self.processor.min_change_pct,
            "max_markets": self.processor.max_markets,
            "hours_back": self.hours_back,
            "output_dir": self.output_dir
        }