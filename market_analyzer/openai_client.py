import os
from openai import OpenAI
from typing import Dict

# Newsletter format templates
NEWSLETTER_FORMATS = {
    "detailed-technical-letter": {
        "name": "Detailed Technical Letter",
        "template": """

Please generate a professional newsletter with this EXACT structure using markdown headers:

# Polymarket Pulse: [Compelling Headline]

## Executive Summary
- 2-3 sentences max summarizing the biggest themes
- Prioritize world events, economic policy, technology, geopolitics, and financial markets
- Deprioritize sports, entertainment, celebrity culture, and trivial prediction topics

## [Theme 1: Descriptive Title]
- Deep analysis of first major theme
- Connect multiple markets under this theme
- Use web search findings for context

**Why it matters for markets and average people:** [Specific implications for both financial markets/prediction markets AND how it affects ordinary people's daily lives]

**What's likely driving this:** [Root causes analysis with real-world context]

**What to expect next:** [Aggressive predictions for next day/week/month - both prediction market prices AND major world events]

## [Theme 2: Descriptive Title]  
- Deep analysis of second major theme
- Connect related market movements
- Real-world context from current events

**Why it matters for markets and average people:** [Specific implications for both financial markets/prediction markets AND how it affects ordinary people's daily lives]

**What's likely driving this:** [Root causes analysis with real-world context]

**What to expect next:** [Aggressive predictions for next day/week/month - both prediction market prices AND major world events]

## [Theme 3: Descriptive Title]
[Continue for 3-6 themes total based on the data, each with the same structure]

## Market Implications & Outlook
- Cross-market connections and correlations
- What to watch for next
- Strategic considerations for traders
- Key upcoming catalysts and events

## Citations
[1] Market Name: Brief explanation of the price change and its significance
[2] Market Name: Brief explanation of the price change and its significance
etc.

REQUIREMENTS:
- 1400-1800 words focused on INSIGHTS and analysis
- Use web search extensively to explain WHY movements happened
- NO "biggest gainers/losers" sections
- NO "by the numbers" sections  
- NO charts or references to charts
- Focus on themes and patterns, not individual market listings
- Professional tone suitable for institutional readers
- Be AGGRESSIVELY PREDICTIVE: Make specific forecasts about what happens next in both markets AND real-world events
- Each theme MUST include the three bolded subsections: "Why it matters for markets and average people", "What's likely driving this", "What to expect next"
- END the newsletter with this exact footer format: "Generated: {timestamp} | {total_markets} markets analyzed"
"""
    },
    "concise-executive-brief": {
        "name": "Concise Executive Brief", 
        "template": """

Please generate a concise executive newsletter with this EXACT structure:

# Polymarket Brief: [Compelling Headline]

## [Theme 1: Descriptive Title]
**What's Happening in the Markets:** [2-3 sentences describing the specific market movements and price changes. Bold key market names, percentages, and dollar amounts.]

**The Bigger Picture:** [2-3 sentences explaining the broader implications and context. Bold key concepts, policy changes, and major trends.]

**What This Means & What to Watch:** [2-3 sentences on impact for average people and key events to monitor. Bold specific dates, events, and impacts.]

**Market Prediction (Speculative):** [1-2 sentences with specific, aggressive predictions about market odds and price movements. Bold specific percentage predictions and timeframes.]

## [Theme 2: Descriptive Title]
**What's Happening in the Markets:** [2-3 sentences describing the specific market movements and price changes. Bold key market names, percentages, and dollar amounts.]

**The Bigger Picture:** [2-3 sentences explaining the broader implications and context. Bold key concepts, policy changes, and major trends.]

**What This Means & What to Watch:** [2-3 sentences on impact for average people and key events to monitor. Bold specific dates, events, and impacts.]

**Market Prediction (Speculative):** [1-2 sentences with specific, aggressive predictions about market odds and price movements. Bold specific percentage predictions and timeframes.]

## [Theme 3: Descriptive Title]
[Continue for 3-6 themes total based on the data, each with the same four-part structure with bolded headers]

## Citations
[1] **Market Name:** Brief explanation of the price change and its significance
[2] **Market Name:** Brief explanation of the price change and its significance
etc.

REQUIREMENTS:
- 800-1200 words total, focused on concise insights
- Each theme section should be exactly 4 paragraphs with the bolded headers shown
- Use **bold formatting** extensively for key terms, numbers, dates, market names, percentages, and important concepts
- Bold all section headers: **What's Happening in the Markets:**, **The Bigger Picture:**, **What This Means & What to Watch:**, **Market Prediction (Speculative):**
- Use web search to provide real-world context
- Write for busy executives who want key insights quickly
- Be AGGRESSIVELY PREDICTIVE with specific market forecasts
- Focus on themes that matter for business and finance
- Prioritize crypto, economics, geopolitics, technology, and major elections
- Avoid sports, entertainment, and trivial topics
- END the newsletter with this exact footer format: "Generated: {timestamp} | {total_markets} markets analyzed"
"""
    }
}


class NewsletterAI:
    def __init__(self):
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.model = "gpt-5"
    
    def generate_newsletter(self, newsletter_data: Dict, format_type: str = "detailed-technical-letter") -> str:
        """Generate a comprehensive newsletter from market data"""
        
        # Create the main prompt based on format
        prompt = self._build_newsletter_prompt(newsletter_data, format_type)
        
        try:
            developer_instructions = """You are a financial market analyst who specializes in prediction markets. You write engaging, informative newsletters about market movements that are accessible to both novice and experienced traders. 

You have access to web search and code interpreter tools:
- Use web search to find recent news, events, or context that might explain market movements
- Use code interpreter to perform statistical analysis, create visualizations, or calculate correlations
- Focus on the implications and context of price movements, not just the numbers

When searching for context, identify the key themes emerging from the market data and search for recent news related to those specific topics. This could include monetary policy, geopolitical developments, technology releases, regulatory changes, election outcomes, economic data, corporate earnings, natural disasters, or any other events that could drive the prediction markets you're analyzing."""
            
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
            
            return response.output_text
            
        except Exception as e:
            print(f"Error generating newsletter: {e}")
            raise
    
    def _build_newsletter_prompt(self, data: Dict, format_type: str = "detailed-technical-letter") -> str:
        """Build the comprehensive prompt for newsletter generation"""
        
        top_markets = data.get("top_markets", [])
        summary_stats = data.get("summary_stats", {})
        config = data.get("config", {})
        
        prompt = f"""
Generate a professional newsletter about significant Polymarket movements in the last {config.get('hours_analyzed', 24)} hours.

NEWSLETTER REQUIREMENTS:
- Write in markdown format
- Include a compelling headline
- Start with executive summary of key movements
- Analyze the top market shifts with context about why they matter
- Include separate sections for biggest gainers and losers
- End with market insights and what to watch
- Use emojis sparingly and professionally
- Focus on implications, not just numbers

MARKET DATA SUMMARY:
- Total markets analyzed: {summary_stats.get('total_markets_analyzed', 0)}
- Significant moves (>{config.get('min_change_threshold', '5%')}): {summary_stats.get('significant_moves', 0)}
- Volume threshold: {config.get('min_volume', 'N/A')}
- Average change magnitude: {summary_stats.get('avg_change_pct', '0%')}
- Generated: {data.get('timestamp', 'Unknown')}

TOP MARKET MOVEMENTS:
"""
        
        # Add ALL top markets details
        for i, market in enumerate(top_markets, 1):
            prompt += f"""
{i}. **{market['question']}**
   - Category: {market['category']}
   - Price: {market['previous_price']} → {market['current_price']} ({market['direction']} {market['change_pct']})
   - Volume: {market['volume']}
   - Closes: {market['end_date']}
"""
        
        if format_type not in NEWSLETTER_FORMATS:
            raise ValueError(f"Unknown format type: {format_type}. Available: {list(NEWSLETTER_FORMATS.keys())}")
        
        # Get template and substitute variables
        template = NEWSLETTER_FORMATS[format_type]["template"]
        summary_stats = data.get("summary_stats", {})
        formatted_template = template.format(
            timestamp=data.get('timestamp', 'Unknown'),
            total_markets=summary_stats.get('total_markets_analyzed', 0)
        )
        
        prompt += formatted_template
        
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
    
