from typing import List, Dict
from datetime import datetime


class MarketDataProcessor:
    def __init__(self, min_volume: float = 10000, min_change_pct: float = 5.0, max_markets: int = 10000):
        self.min_volume = min_volume
        self.min_change_pct = min_change_pct
        self.max_markets = max_markets
    
    def rank_by_significance(self, markets: List[Dict]) -> List[Dict]:
        """Rank markets by significance of price changes"""
        # Filter markets with meaningful changes
        significant_markets = [
            market for market in markets
            if abs(market.get("price_change_pct", 0)) >= self.min_change_pct
            and market.get("volume", 0) >= self.min_volume
        ]
        
        # Sort by absolute percentage change (biggest moves first)
        significant_markets.sort(
            key=lambda x: abs(x.get("price_change_pct", 0)), 
            reverse=True
        )
        
        return significant_markets[:self.max_markets]
    
    def categorize_markets(self, markets: List[Dict]) -> Dict[str, List[Dict]]:
        """Categorize markets by type/category"""
        categories = {}
        
        for market in markets:
            category = market.get("category", "Other").title()
            if category not in categories:
                categories[category] = []
            categories[category].append(market)
            
        return categories
    
    def format_market_summary(self, market: Dict) -> Dict[str, str]:
        """Format a single market into a summary dict"""
        current_price = market.get("current_yes_price", 0)
        historical_price = market.get("historical_yes_price", 0)
        change_pct = market.get("price_change_pct", 0)
        volume = market.get("volume", 0)
        
        # Determine direction
        direction = "📈" if change_pct > 0 else "📉"
        direction_text = "increased" if change_pct > 0 else "decreased"
        
        # Format volume
        volume_str = self._format_volume(volume)
        
        return {
            "question": market.get("question", "Unknown"),
            "category": market.get("category", "Other").title(),
            "current_price": f"{current_price:.1%}",
            "previous_price": f"{historical_price:.1%}",
            "change_pct": f"{abs(change_pct):.1f}%",
            "direction": direction,
            "direction_text": direction_text,
            "volume": volume_str,
            "market_slug": market.get("market_slug", ""),
            "end_date": self._format_date(market.get("end_date_iso", "")),
            "raw_change": change_pct
        }
    
    def create_newsletter_data(self, markets: List[Dict]) -> Dict:
        """Create structured data for newsletter generation"""
        # Rank markets by significance
        top_markets = self.rank_by_significance(markets)
        
        # Format market summaries
        formatted_markets = [self.format_market_summary(market) for market in top_markets]
        
        # Categorize markets
        categorized = self.categorize_markets(top_markets)
        
        # Calculate summary stats
        total_markets_analyzed = len(markets)
        significant_moves = len(formatted_markets)
        avg_change = sum(abs(m.get("raw_change", 0)) for m in formatted_markets) / len(formatted_markets) if formatted_markets else 0
        
        # Split into gainers and losers
        gainers = [m for m in formatted_markets if m["raw_change"] > 0]
        losers = [m for m in formatted_markets if m["raw_change"] < 0]
        
        return {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M UTC"),
            "summary_stats": {
                "total_markets_analyzed": total_markets_analyzed,
                "significant_moves": significant_moves,
                "avg_change_pct": f"{avg_change:.1f}%",
                "gainers_count": len(gainers),
                "losers_count": len(losers)
            },
            "top_markets": formatted_markets,
            "gainers": gainers[:5],  # Top 5 gainers
            "losers": losers[:5],   # Top 5 losers
            "by_category": categorized,
            "config": {
                "hours_analyzed": 24,
                "min_volume": self._format_volume(self.min_volume),
                "min_change_threshold": f"{self.min_change_pct}%"
            }
        }
    
    def _format_volume(self, volume: float) -> str:
        """Format volume in human-readable format"""
        if volume >= 1_000_000:
            return f"${volume/1_000_000:.1f}M"
        elif volume >= 1_000:
            return f"${volume/1_000:.0f}K"
        else:
            return f"${volume:.0f}"
    
    def _format_date(self, date_str: str) -> str:
        """Format ISO date string to readable format"""
        try:
            date = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            return date.strftime("%B %d, %Y")
        except (ValueError, TypeError):
            return "Unknown"
    
    def generate_market_insights(self, markets: List[Dict]) -> List[str]:
        """Generate key insights from market data"""
        if not markets:
            return ["No significant market movements detected."]
            
        insights = []
        
        # Identify biggest mover
        biggest_mover = max(markets, key=lambda x: abs(x.get("price_change_pct", 0)))
        insights.append(
            f"The biggest price movement was in '{biggest_mover.get('question', 'Unknown')}' "
            f"with a {abs(biggest_mover.get('price_change_pct', 0)):.1f}% change."
        )
        
        # Category analysis
        categories = self.categorize_markets(markets)
        if len(categories) > 1:
            most_active_category = max(categories.keys(), key=lambda k: len(categories[k]))
            insights.append(
                f"The {most_active_category} category saw the most activity with "
                f"{len(categories[most_active_category])} significant moves."
            )
        
        # Volume analysis
        high_volume_markets = [m for m in markets if m.get("volume", 0) > 100000]
        if high_volume_markets:
            insights.append(
                f"{len(high_volume_markets)} markets with over $100K volume saw significant price changes."
            )
        
        return insights