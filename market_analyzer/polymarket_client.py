import requests
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional


class PolymarketClient:
    def __init__(self):
        self.base_url = "https://clob.polymarket.com"
        self.gamma_url = "https://gamma-api.polymarket.com"
        
    def get_all_markets(self, limit: Optional[int] = None) -> List[Dict]:
        """Fetch all active markets with pagination"""
        all_markets = []
        
        # Try Gamma API first for current markets with pagination
        try:
            url = f"{self.gamma_url}/markets"
            offset = 0
            page_size = 100
            
            while True:
                params = {
                    "active": True,
                    "closed": False,
                    "volume_num_min": 1000,  # Get markets with some volume
                    "limit": page_size,
                    "offset": offset
                }
                
                response = requests.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                if not data:  # No more data
                    break
                
                # Convert gamma format to CLOB format
                for market in data:
                    # Extract tokens from clobTokenIds if available
                    tokens = []
                    if "clobTokenIds" in market and market["clobTokenIds"]:
                        try:
                            clob_token_ids = json.loads(market["clobTokenIds"])
                            outcomes = json.loads(market.get("outcomes", '["Yes", "No"]'))
                            for i, token_id in enumerate(clob_token_ids):
                                if i < len(outcomes):
                                    tokens.append({
                                        "token_id": str(token_id),
                                        "outcome": outcomes[i]
                                    })
                        except (json.JSONDecodeError, IndexError):
                            pass
                    
                    converted_market = {
                        "condition_id": market.get("conditionId", ""),
                        "question_id": market.get("questionID", ""),
                        "question": market.get("question", ""),
                        "market_slug": market.get("slug", ""),
                        "end_date_iso": market.get("endDate", ""),
                        "category": market.get("category", "Other"),
                        "active": market.get("active", True),
                        "closed": market.get("closed", False),
                        "volume": float(market.get("volumeNum", market.get("volume", 0))),
                        "tokens": tokens,
                        # Copy over price data
                        "outcomePrices": market.get("outcomePrices", ""),
                        "outcomes": market.get("outcomes", '["Yes", "No"]'),
                        "lastTradePrice": market.get("lastTradePrice", 0),
                        "oneDayPriceChange": market.get("oneDayPriceChange", 0),
                        "oneWeekPriceChange": market.get("oneWeekPriceChange", 0),
                        "oneMonthPriceChange": market.get("oneMonthPriceChange", 0)
                    }
                    
                    all_markets.append(converted_market)
                    
                    # Check if we've hit the user-specified limit
                    if limit and len(all_markets) >= limit:
                        return all_markets[:limit]
                
                # If we got less than page_size results, we've reached the end
                if len(data) < page_size:
                    break
                    
                offset += page_size
                
            return all_markets
            
        except requests.RequestException as e:
            print(f"Error fetching from Gamma API: {e}")
            print("   Falling back to CLOB API...")
        
        # Fallback to CLOB API
        next_cursor = ""
        
        while True:
            url = f"{self.base_url}/markets"
            params = {}
            if next_cursor and next_cursor != "LTE=":
                params["next_cursor"] = next_cursor
                
            try:
                response = requests.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                all_markets.extend(data.get("data", []))
                
                # Check if we've hit the limit
                if limit and len(all_markets) >= limit:
                    all_markets = all_markets[:limit]
                    break
                
                next_cursor = data.get("next_cursor", "")
                
                if next_cursor == "LTE=" or not next_cursor:
                    break
                    
            except requests.RequestException as e:
                print(f"Error fetching markets: {e}")
                break
                
        return all_markets
    
    def get_market_prices(self, token_ids: List[str]) -> Dict[str, float]:
        """Get current prices for multiple token IDs"""
        if not token_ids:
            return {}
            
        url = f"{self.base_url}/prices"
        params = {"token_ids": ",".join(token_ids)}
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error fetching prices: {e}")
            return {}
    
    def get_historical_prices(self, token_id: str, hours_back: int = 14) -> List[Dict]:
        """Get historical price data for a token"""
        end_time = int(time.time())
        start_time = end_time - (hours_back * 3600)
        
        url = f"{self.base_url}/prices-history"
        params = {
            "market": token_id,
            "startTs": start_time,
            "endTs": end_time,
            "fidelity": "1h"  # 1 hour intervals
        }
        
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json().get("history", [])
        except requests.RequestException as e:
            print(f"Error fetching historical prices for {token_id}: {e}")
            return []
    
    def get_market_volume(self, condition_id: str) -> float:
        """Get market volume from Gamma API"""
        url = f"{self.gamma_url}/markets/{condition_id}"
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            return float(data.get("volume", 0))
        except requests.RequestException as e:
            print(f"Error fetching volume for {condition_id}: {e}")
            return 0.0
    
    def filter_active_markets(self, markets: List[Dict], min_volume: float = 10000) -> List[Dict]:
        """Filter for active, non-daily markets with minimum volume"""
        filtered_markets = []
        
        print(f"   Filtering {len(markets)} markets...")
        active_count = 0
        not_closed_count = 0
        future_end_count = 0
        
        for market in markets:
            # Just require that it has a question and condition_id
            if not market.get("question") or not market.get("condition_id"):
                continue
            
            # For now, let's be less strict about closed/active status
            if market.get("active", False):
                active_count += 1
                
            if not market.get("closed", True):  # Assume not closed if not specified
                not_closed_count += 1
                
            # Skip daily markets - check if end date is within 48 hours
            skip_daily = False
            try:
                end_date_str = market.get("end_date_iso")
                if end_date_str:
                    end_date = datetime.fromisoformat(end_date_str.replace("Z", "+00:00"))
                    if end_date < datetime.now().astimezone() + timedelta(hours=48):
                        skip_daily = True
                if not skip_daily:
                    future_end_count += 1
            except (ValueError, TypeError, AttributeError):
                future_end_count += 1
                
            if skip_daily:
                continue
                
            # Use the volume from Gamma API if available
            market["volume"] = market.get("volume", 0)
            if market["volume"] < min_volume:
                continue
                
            filtered_markets.append(market)
            
        print(f"   Active: {active_count}, Not closed: {not_closed_count}, Future end: {future_end_count}, Final: {len(filtered_markets)}")
        return filtered_markets
    
    def calculate_price_changes(self, markets: List[Dict]) -> List[Dict]:
        """Calculate price changes for markets over the specified time period"""
        markets_with_changes = []
        
        for market in markets:
            # Get both YES and NO tokens for binary markets
            tokens = market.get("tokens", [])
            if len(tokens) != 2:
                continue
            
            # For now, use price change data from the Gamma API if available
            current_yes_price = None
            historical_price = None
            
            # Try to extract prices from outcomePrices
            try:
                if "outcomePrices" in market and market["outcomePrices"]:
                    outcome_prices = json.loads(market["outcomePrices"])
                    outcomes = json.loads(market.get("outcomes", '["Yes", "No"]'))
                    # Find the Yes token price
                    for i, outcome in enumerate(outcomes):
                        if outcome == "Yes" and i < len(outcome_prices):
                            current_yes_price = float(outcome_prices[i])
                            break
            except (json.JSONDecodeError, ValueError, IndexError):
                pass
                
            # If we couldn't get price from outcomePrices, try the price change fields
            if current_yes_price is None and "lastTradePrice" in market:
                current_yes_price = float(market["lastTradePrice"])
                
            # If still no price, skip this market
            if current_yes_price is None or current_yes_price == 0:
                continue
                
            # Calculate historical price based on available price change data
            price_change_pct = 0
            
            # Use ONLY 1-week price changes for consistency in weekly analysis
            # Skip markets that don't have 1-week data to maintain data integrity
            if not market.get("oneWeekPriceChange"):
                continue
                
            historical_price = current_yes_price - float(market["oneWeekPriceChange"])
            if historical_price > 0:
                price_change_pct = (float(market["oneWeekPriceChange"]) / historical_price) * 100
            else:
                continue
            
            # If we have no historical data, skip this market
            if historical_price is None or abs(price_change_pct) < 0.1:
                continue
                
            market["current_yes_price"] = current_yes_price
            market["historical_yes_price"] = historical_price
            market["price_change"] = current_yes_price - historical_price
            market["price_change_pct"] = price_change_pct
            
            markets_with_changes.append(market)
                
        return markets_with_changes