import os
from openai import OpenAI
from typing import Dict

# Newsletter format templates
NEWSLETTER_FORMATS = {
    "institutional-analysis": {
        "name": "Institutional Analysis",
        "developer_instructions": """You are a financial market analyst who specializes in prediction markets. You write engaging, informative newsletters about market movements that are accessible to both novice and experienced traders. 

You have access to web search and code interpreter tools:
- Use web search to find recent news, events, or context that might explain market movements
- Use code interpreter to perform statistical analysis, create visualizations, or calculate correlations
- Focus on the implications and context of price movements, not just the numbers

When searching for context, identify the key themes emerging from the market data and search for recent news related to those specific topics. This could include monetary policy, geopolitical developments, technology releases, regulatory changes, election outcomes, economic data, corporate earnings, natural disasters, or any other events that could drive the prediction markets you're analyzing.

Write in a professional tone suitable for institutional readers who want comprehensive analysis and insights.""",
        "template": """

Please generate a professional newsletter with this EXACT structure using markdown headers:

# Polymarket Analysis: [Compelling Headline]

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
"""
    },
    "executive-brief": {
        "name": "Executive Brief",
        "developer_instructions": """You are a financial market analyst who specializes in prediction markets. You write clear, accessible briefings for intelligent but busy readers who want to stay informed about major market movements and world events.

You have access to web search and code interpreter tools:
- Use web search to find recent news, events, or context that might explain market movements
- Use code interpreter to perform statistical analysis, create visualizations, or calculate correlations
- Focus on translating complex market data into digestible insights

When searching for context, identify the key themes emerging from the market data and search for recent news related to those specific topics. This could include monetary policy, geopolitical developments, technology releases, regulatory changes, election outcomes, economic data, corporate earnings, natural disasters, or any other events that could drive the prediction markets you're analyzing.

Write for an intelligent general audience (executives, curious investors, informed citizens) using plain language. Avoid jargon and explain complex concepts clearly. Focus on what matters for both markets AND average people's daily lives.""",
        "template": """

Please generate a concise executive newsletter with this EXACT structure:

# Polymarket Analysis: [Compelling Headline]

## 1. [Theme Title]: The New Wall Street Mainstay
**What's Happening in the Markets:** [2-3 sentences describing specific market movements in plain language. Focus on the story, not jargon. Bold key numbers and dates.]

**The Bigger Picture:** [2-3 sentences explaining what this means for the world and economy in accessible terms. Avoid technical jargon. Bold major concepts and changes.]

**What This Means & What to Watch:** [2-3 sentences covering impact on both markets AND average people's daily lives. Bold key events and dates to monitor.]

**Market Prediction (Speculative):** [1-2 sentences with specific, aggressive predictions. Bold percentage ranges and timeframes. Make it accessible.]

## 2. [Theme Title]: A Tug-of-War Between Lower Rates and Higher Walls  
**What's Happening in the Markets:** [2-3 sentences describing specific market movements in plain language. Focus on the story, not jargon. Bold key numbers and dates.]

**The Bigger Picture:** [2-3 sentences explaining what this means for the world and economy in accessible terms. Avoid technical jargon. Bold major concepts and changes.]

**What This Means & What to Watch:** [2-3 sentences covering impact on both markets AND average people's daily lives. Bold key events and dates to monitor.]

**Market Prediction (Speculative):** [1-2 sentences with specific, aggressive predictions. Bold percentage ranges and timeframes. Make it accessible.]

## 3. [Theme Title]: The Fragile State of Stability
[Continue for 3-6 themes total based on the data, each with the same four-part structure. Use descriptive, accessible titles like "The AI Race", "World Elections", etc.]

## Citations
[1] **Market Name:** Brief explanation of the price change and its significance
[2] **Market Name:** Brief explanation of the price change and its significance
etc.

REQUIREMENTS:
- 800-1200 words total, prioritizing clarity and digestibility over data density
- Write for intelligent but busy general readers (executives, curious investors, informed citizens)
- Use plain language and avoid jargon like "gamma-driven", "crypto beta", "hardening positions"
- Each theme section should be exactly 4 paragraphs with the bolded headers shown
- Use **bold formatting** for key terms, numbers, dates, but don't overwhelm with technical data
- Focus on themes that connect to real-world events people care about
- Explain WHY movements matter for both financial markets AND ordinary people's lives
- Be AGGRESSIVELY PREDICTIVE but make predictions accessible and understandable
- Prioritize world events, economics, technology, geopolitics that affect daily life
"""
    },
    "macro-outlook": {
        "name": "Macro & Geopolitical 7-Day Outlook",
        "developer_instructions": """You are a senior financial analyst specializing in prediction markets with deep expertise in macroeconomics, geopolitics, and global market dynamics. You write comprehensive briefings that connect prediction market movements to broader world events for sophisticated readers who need to understand both market implications and real-world consequences.

You have access to web search and code interpreter tools:
- Use web search extensively to find recent news, economic data releases, policy announcements, and geopolitical developments
- Use code interpreter for statistical analysis, correlations, and market pattern recognition
- Focus on identifying systemic connections between market movements and global events
- Prioritize macroeconomic themes, central bank policy, geopolitical developments, and technology disruption

Your analysis should demonstrate sophisticated understanding of how prediction markets reflect and predict real-world outcomes. Connect seemingly disparate market movements under broader thematic frameworks. Be aggressively predictive with specific timeframes and probability ranges.

Write for institutional investors, policy analysts, and sophisticated market participants who understand complex market dynamics and want actionable insights for both investment decisions and geopolitical risk assessment.""",
        "template": """

Generate a comprehensive market outlook with this EXACT structure:

# Polymarket Analysis: Global Markets & World Events: A 7-Day Outlook

Key events in macroeconomics, geopolitics, and technology are poised to drive significant market moves this week. Here's a concise breakdown of what to watch.

### **[Primary Theme Title]: [Specific Market Setup Description]**

* **The Setup:** [2-3 sentences describing specific market movements, odds changes, and positioning. Include exact market names, percentage changes, and current probability levels. MUST include brief speculation about WHY these markets moved - economic data, policy announcements, geopolitical events, etc.]
* **Why It Matters (The Big Picture):** [2-3 sentences connecting this to broader economic or geopolitical trends. Explain systemic implications beyond just the specific markets. Use **bold** for key terms sparingly.]
* **Market Prediction (Next 7 Days):** [2-4 sentences with aggressive, specific predictions. Include exact dates, probability ranges, and threshold levels. Reference specific upcoming catalysts.]

---

### **[Secondary Theme Title]: [Descriptive Setup]**

* **The Setup:** [2-3 sentences with market data AND speculation about drivers]
* **Why It Matters (The Big Picture):** [2-3 sentences on broader implications with occasional **bold** key terms]
* **Market Prediction (Next 7 Days):** [2-4 sentences with specific forecasts and catalyst dates]

---

### **[Third Theme Title]: [Setup Description]**

* **The Setup:** [Continue pattern for 3-5 themes total based on data significance]
* **Why It Matters (The Big Picture):** [Use folded bullet structure when helpful:
  - Sub-point about economic impact
  - Sub-point about market implications]
* **Market Prediction (Next 7 Days):** [Aggressive predictions with dates and probabilities]

---

### **[Final Theme Title]: [Setup Description]**

* **The Setup:** [Final major theme analysis with market movements and speculation]
* **Why It Matters (The Big Picture):** [Broader implications with **bold** key concepts]
* **Market Prediction (Next 7 Days):** [Specific predictions for next week]

## Citations

[1] **Market Name:** Brief explanation of the price change and its significance
[2] **Market Name:** Brief explanation of the price change and its significance
[Continue numbering for all major markets referenced]

REQUIREMENTS:
- 1200-1600 words focused on sophisticated market-world event connections
- Each theme must follow the exact three-bullet structure: Setup, Why It Matters, Market Prediction
- Use horizontal rule separators (---) between each theme section
- In "The Setup" sections, ALWAYS include speculation about what drove the market movements
- Use **bold** sparingly for key terms and concepts, not overwhelming the text
- Use folded bullet points (sub-bullets) when helpful for readability in "Why It Matters" sections
- Be AGGRESSIVELY PREDICTIVE with specific dates, probability ranges, and threshold levels
- Focus on macroeconomic themes: Fed policy, geopolitics, technology disruption, regulatory changes
- Connect multiple related markets under each thematic section
- Include specific upcoming catalyst dates and events
- Use web search to provide current context for why these movements are happening
- Professional tone for institutional/sophisticated readers
- END with a Citations section listing all major markets referenced with brief explanations
"""
    }
}


class NewsletterAI:
    def __init__(self):
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.model = "gpt-5"
    
    def generate_newsletter(self, newsletter_data: Dict, format_type: str = "institutional-analysis") -> str:
        """Generate a comprehensive newsletter from market data"""
        
        # Create the main prompt based on format
        prompt = self._build_newsletter_prompt(newsletter_data, format_type)
        
        try:
            # Get format-specific developer instructions
            if format_type not in NEWSLETTER_FORMATS:
                raise ValueError(f"Unknown format type: {format_type}. Available: {list(NEWSLETTER_FORMATS.keys())}")
            
            developer_instructions = NEWSLETTER_FORMATS[format_type]["developer_instructions"]
            
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
        
        if format_type not in NEWSLETTER_FORMATS:
            raise ValueError(f"Unknown format type: {format_type}. Available: {list(NEWSLETTER_FORMATS.keys())}")
        
        # Get template (no substitution needed since footer is programmatic)
        template = NEWSLETTER_FORMATS[format_type]["template"]
        prompt += template
        
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
    
