import os
from openai import OpenAI
from typing import Dict
from .newsletter_formats import DEVELOPER_INSTRUCTIONS, NEWSLETTER_TEMPLATE
from .topic_config import get_display_name

class NewsletterAI:
    def __init__(self):
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.model = "gpt-5"
    
    def generate_newsletter(self, newsletter_data: Dict, format_type: str = "institutional-analysis") -> str:
        """Generate a comprehensive newsletter from market data"""
        
        # Create the main prompt based on format
        prompt = self._build_newsletter_prompt(newsletter_data, format_type)
        
        try:
            # Use simplified developer instructions
            developer_instructions = DEVELOPER_INSTRUCTIONS
            
            response = self.client.responses.create(
                model=self.model,
                instructions=developer_instructions,
                input=prompt,
                tools=[
                    {"type": "web_search_preview"},
                    {
                        "type": "code_interpreter",
                        "container": {"type": "auto"}
                    }
                ],
                reasoning={
                    "effort": "high"
                }
            )
            
            # Add programmatic footer
            newsletter_content = response.output_text
            summary_stats = newsletter_data.get("summary_stats", {})
            timestamp = newsletter_data.get("timestamp", "Unknown")
            total_markets = summary_stats.get("total_markets_analyzed", 0)
            
            footer = f"\n\n---\n\n*Generated: {timestamp} | {total_markets} markets analyzed*"
            
            return newsletter_content + footer
            
        except Exception as e:
            print(f"Error generating newsletter: {e}")
            raise
    
    def generate_newsletter_with_context(self, newsletter_data: Dict, format_type: str = "tech-outlook", topic_context: str = "", topics: list = None) -> str:
        """Generate newsletter with specific topic context"""
        
        # Create the main prompt with topic context
        prompt = self._build_newsletter_prompt_with_context(newsletter_data, format_type, topic_context)
        
        try:
            # Get base developer instructions and add topic context
            base_instructions = DEVELOPER_INSTRUCTIONS
            
            # Enhance instructions with topic context
            enhanced_instructions = f"""{base_instructions}

TOPIC FOCUS: {topic_context}

When analyzing the market data, prioritize insights that align with the subscriber's topic interests while maintaining comprehensive coverage of all significant market movements."""
            
            response = self.client.responses.create(
                model=self.model,
                instructions=enhanced_instructions,
                input=prompt,
                tools=[
                    {"type": "web_search_preview"},
                    {
                        "type": "code_interpreter",
                        "container": {"type": "auto"}
                    }
                ],
                reasoning={
                    "effort": "high"
                }
            )
            
            # Add programmatic footer
            newsletter_content = response.output_text
            summary_stats = newsletter_data.get("summary_stats", {})
            timestamp = newsletter_data.get("timestamp", "Unknown")
            total_markets = summary_stats.get("total_markets_analyzed", 0)
            
            # Include topics in footer if provided
            footer_parts = [f"Generated: {timestamp}", f"{total_markets} markets analyzed"]
            
            if topics:
                topic_names = [get_display_name(topic) for topic in topics]
                footer_parts.append(f"Topics: {', '.join(topic_names)}")
            
            footer = f"\n\n---\n\n*{' | '.join(footer_parts)}*"
            
            return newsletter_content + footer
            
        except Exception as e:
            print(f"Error generating newsletter with context: {e}")
            raise
    
    def _build_newsletter_prompt_with_context(self, data: Dict, format_type: str, topic_context: str) -> str:
        """Build newsletter prompt with topic context"""
        base_prompt = self._build_newsletter_prompt(data, format_type)
        
        if topic_context:
            context_addition = f"""

SUBSCRIBER TOPIC FOCUS: {topic_context}

Please emphasize insights and analysis that align with these topic areas while maintaining comprehensive coverage of all significant market movements."""
            return base_prompt + context_addition
        
        return base_prompt
    
    def _build_newsletter_prompt(self, data: Dict, format_type: str = "institutional-analysis") -> str:
        """Build the comprehensive prompt for newsletter generation"""
        
        top_markets = data.get("top_markets", [])
        summary_stats = data.get("summary_stats", {})
        config = data.get("config", {})
        
        prompt = f"""
Generate a professional newsletter about significant Polymarket movements in the last {config.get('hours_analyzed', 24)} hours.

MARKET DATA SUMMARY:
- Total markets analyzed: {summary_stats.get('total_markets_analyzed', 0)}
- Significant moves (>{config.get('min_change_threshold', '5%')}): {summary_stats.get('significant_moves', 0)}
- Volume threshold: {config.get('min_volume', 'N/A')}
- Average change magnitude: {summary_stats.get('avg_change_pct', '0%')}
- Generated: {data.get('timestamp', 'Unknown')}

TOP MARKET MOVEMENTS:
"""
        
        # Add ALL top markets details - same format for all newsletter types
        for i, market in enumerate(top_markets, 1):
            prompt += f"""
{i}. **{market['question']}**
   - Category: {market['category']}
   - Price: {market['previous_price']} → {market['current_price']} ({market['direction']} {market['change_pct']})
   - Volume: {market['volume']}
   - Closes: {market['end_date']}
"""
        
        # Add the newsletter template
        prompt += NEWSLETTER_TEMPLATE
        
        return prompt
    
    def generate_market_analysis(self, market_data: Dict) -> str:
        """Generate detailed analysis for a specific market"""
        
        prompt = f"""
Analyze this Polymarket movement and provide context:

Market: {market_data.get('question', 'Unknown')}
Category: {market_data.get('category', 'Unknown')}
Price Change: {market_data.get('previous_price', '0%')} → {market_data.get('current_price', '0%')}
Change: {market_data.get('direction', '')} {market_data.get('change_pct', '0%')}
Volume: {market_data.get('volume', 'Unknown')}
End Date: {market_data.get('end_date', 'Unknown')}

Provide a 2-3 paragraph analysis covering:
1. What this market is about and why it matters
2. What might have caused this price movement
3. What this shift suggests about market sentiment
4. Any relevant context or recent events

Keep it informative but accessible to general readers.
"""
        
        try:            
            response = self.client.responses.create(
                model=self.model,
                instructions="You are a prediction market analyst who explains market movements with context and insight.",
                input=prompt,
                reasoning={
                    "effort": "high"
                }
            )
            
            return response.output_text
            
        except Exception as e:
            print(f"Error generating market analysis: {e}")
            return f"Analysis unavailable for {market_data.get('question', 'this market')}"
    
