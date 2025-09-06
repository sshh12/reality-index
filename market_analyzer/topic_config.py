"""
Topic Configuration - Single Source of Truth

This file defines all newsletter topics with their display names and descriptions.
Used across the entire application for consistency.
"""

from typing import Dict, List, NamedTuple


class TopicConfig(NamedTuple):
    """Configuration for a newsletter topic"""
    key: str           # URL/database friendly identifier
    display_name: str  # Human-readable name for UI
    description: str   # Description for subscribers
    prompt_context: str # Context for AI newsletter generation


# All available topics - single source of truth
TOPICS = {
    'us_politics': TopicConfig(
        key='us_politics',
        display_name='US Politics',
        description='US politics, elections, domestic policy, and American political developments',
        prompt_context='Focus on US domestic politics, presidential and congressional elections, American policy decisions, Supreme Court cases, state-level political developments, and domestic governance issues affecting the United States.'
    ),
    
    'world_politics': TopicConfig(
        key='world_politics', 
        display_name='World Politics',
        description='International relations, geopolitics, global conflicts, and foreign affairs',
        prompt_context='Emphasize international relations, geopolitical conflicts, global diplomacy, foreign policy decisions, international treaties, global security issues, and relationships between nations and international organizations.'
    ),
    
    'sports': TopicConfig(
        key='sports',
        display_name='Sports',
        description='Sports betting markets, player performance, team outcomes, and athletic competitions',
        prompt_context='Highlight sports betting markets, player performance predictions, team success probabilities, championship outcomes, draft predictions, trade possibilities, and major sporting event results across all professional and amateur athletics.'
    ),
    
    'crypto': TopicConfig(
        key='crypto',
        display_name='Crypto', 
        description='Cryptocurrency prices, blockchain adoption, DeFi developments, and digital asset trends',
        prompt_context='Focus on cryptocurrency price predictions, blockchain technology adoption, DeFi protocol developments, NFT market trends, regulatory decisions affecting digital assets, and major cryptocurrency project launches or updates.'
    ),
    
    'economics': TopicConfig(
        key='economics',
        display_name='Economics',
        description='Economic indicators, market conditions, inflation, interest rates, and financial markets', 
        prompt_context='Emphasize economic indicators like GDP, inflation, unemployment, Federal Reserve decisions, interest rate changes, stock market performance, recession predictions, and major financial market developments.'
    ),
    
    'tech': TopicConfig(
        key='tech',
        display_name='Tech',
        description='Technology companies, product launches, industry trends, and general tech innovation',
        prompt_context='Highlight major technology company developments, product launches, IPO predictions, tech industry mergers and acquisitions, startup valuations, and broader technology adoption trends across industries.'
    ),
    
    'ai': TopicConfig(
        key='ai', 
        display_name='AI',
        description='Artificial intelligence breakthroughs, AI company developments, and machine learning advances',
        prompt_context='Focus specifically on artificial intelligence breakthroughs, AI company funding and developments, machine learning advances, AI regulation and policy, AI safety discussions, and predictions about AI capability milestones.'
    ),
    
    'culture': TopicConfig(
        key='culture',
        display_name='Culture',
        description='Entertainment, movies, celebrity events, cultural trends, and pop culture phenomena',
        prompt_context='Emphasize entertainment industry predictions, movie and show success rates, celebrity news and events, cultural trend forecasts, awards show outcomes, and broader pop culture phenomenon predictions.'
    )
}


def get_topic_keys() -> List[str]:
    """Get list of all topic keys"""
    return list(TOPICS.keys())


def get_topic_display_names() -> Dict[str, str]:
    """Get mapping of topic keys to display names"""
    return {key: config.display_name for key, config in TOPICS.items()}


def get_topic_descriptions() -> Dict[str, str]:
    """Get mapping of topic keys to descriptions"""
    return {key: config.description for key, config in TOPICS.items()}


def get_topic_prompt_contexts() -> Dict[str, str]:
    """Get mapping of topic keys to AI prompt contexts"""
    return {key: config.prompt_context for key, config in TOPICS.items()}


def get_display_name(topic_key: str) -> str:
    """Get display name for a topic key"""
    return TOPICS.get(topic_key, TopicConfig('', topic_key.title(), '', '')).display_name


def get_prompt_context_for_topics(topic_keys: List[str]) -> str:
    """Generate AI prompt context for multiple topics"""
    if not topic_keys:
        return "Provide comprehensive coverage of all prediction market developments."
    
    contexts = []
    for key in topic_keys:
        if key in TOPICS:
            contexts.append(TOPICS[key].prompt_context)
    
    if not contexts:
        return "Provide comprehensive coverage of all prediction market developments."
    
    if len(contexts) == 1:
        return contexts[0]
    
    combined = "Focus on the following areas: " + " Additionally, ".join(contexts)
    return combined + " Ensure balanced coverage across these topic areas while maintaining the newsletter's prediction market analysis focus."