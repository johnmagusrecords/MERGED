import json
import logging
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List

import numpy as np
import openai
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChatGPTAnalyst:
    """ChatGPT integration for enhanced market analysis"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            self.logger.warning(
                "OpenAI API key not found. ChatGPT integration will not function."
            )
        else:
            openai.api_key = self.api_key

        self.model = "gpt-4-turbo"  # Using the most advanced model available
        self.cache = {}  # Cache results to minimize API calls
        self.cache_duration = 60 * 15  # 15 minutes cache duration
        self.max_retries = 3
        self.retry_delay = 5  # seconds

    def analyze_market(
        self,
        symbol: str,
        timeframe: str,
        data: pd.DataFrame,
        news_items: List[Dict],
        indicators: Dict,
    ) -> Dict:
        """
        Analyze market conditions using ChatGPT

        Args:
            symbol: The trading symbol (e.g., 'BTCUSD')
            timeframe: The trading timeframe (e.g., '1h', '4h')
            data: OHLCV data
            news_items: Recent news related to the symbol
            indicators: Technical indicators

        Returns:
            Dict containing the analysis results
        """
        try:
            cache_key = f"{symbol}_{timeframe}_{datetime.now().strftime('%Y-%m-%d_%H')}"
            if cache_key in self.cache:
                cache_item = self.cache[cache_key]
                if datetime.now() - cache_item["timestamp"] < timedelta(
                    seconds=self.cache_duration
                ):
                    return cache_item["result"]

            if not self.api_key:
                return {
                    "error": "OpenAI API key not configured",
                    "sentiment": "neutral",
                    "confidence": 0.5,
                    "trading_bias": "neutral",
                    "reasoning": "ChatGPT integration not available",
                }

            # Prepare market data for the prompt
            market_context = self._prepare_market_context(
                symbol, timeframe, data, indicators
            )

            # Prepare news summary
            news_summary = self._prepare_news_summary(news_items)

            # Construct the prompt
            prompt = self._construct_analysis_prompt(
                symbol, timeframe, market_context, news_summary
            )

            # Get response from ChatGPT
            response = self._get_chatgpt_response(prompt)

            # Parse the response
            analysis = self._parse_analysis_response(response)

            # Cache the result
            self.cache[cache_key] = {"timestamp": datetime.now(), "result": analysis}

            return analysis

        except Exception as e:
            self.logger.error(f"Error in ChatGPT market analysis: {str(e)}")
            return {
                "error": str(e),
                "sentiment": "neutral",
                "confidence": 0.5,
                "trading_bias": "neutral",
                "reasoning": "Error performing analysis",
            }

    def analyze_trading_opportunity(
        self,
        symbol: str,
        timeframe: str,
        entry_price: float,
        stop_loss: float,
        take_profit: float,
        direction: str,
        data: pd.DataFrame,
        indicators: Dict,
    ) -> Dict:
        """
        Evaluate a specific trading opportunity

        Args:
            symbol: The trading symbol
            timeframe: The trading timeframe
            entry_price: The entry price
            stop_loss: The stop loss level
            take_profit: The take profit level
            direction: 'long' or 'short'
            data: OHLCV data
            indicators: Technical indicators

        Returns:
            Dict containing the analysis results
        """
        try:
            if not self.api_key:
                return {
                    "rating": 5,  # Neutral rating
                    "confidence": 0.5,
                    "reasoning": "ChatGPT integration not available",
                    "suggestions": [],
                }

            # Prepare market data
            self._prepare_market_context(
                symbol, timeframe, data, indicators
            )

            # Calculate risk-reward ratio
            if direction.lower() == "long":
                risk = entry_price - stop_loss
                reward = take_profit - entry_price
            else:
                risk = stop_loss - entry_price
                reward = entry_price - take_profit

            risk_reward_ratio = reward / risk if risk > 0 else 0

            # Construct the prompt
            prompt = f"""
You are an expert trading analyst. Assess the following trade opportunity:

Symbol: {symbol}
Timeframe: {timeframe}
Direction: {direction}
Entry Price: {entry_price}
Stop Loss: {stop_loss}
Take Profit: {take_profit}
Risk-Reward Ratio: {risk_reward_ratio:.2f}

Recent Market Data:
Current Price: {data['close'].iloc[-1]}
Previous Close: {data['close'].iloc[-2]}
Price Change: {((data['close'].iloc[-1] / data['close'].iloc[-2]) - 1) * 100:.2f}%

Technical Indicators:
{json.dumps(indicators, indent=2)}

Rate this trade opportunity on a scale of 1-10, where:
1-3: Poor opportunity with high risk
4-6: Neutral opportunity
7-10: Excellent opportunity with favorable risk-reward

Provide a detailed reasoning for your rating and suggestions to improve the trade.

Format your response as JSON:
{{
  "rating": number,
  "confidence": number,
  "reasoning": "string",
  "suggestions": ["string"]
}}
"""

            # Get response from ChatGPT
            response = self._get_chatgpt_response(prompt)

            # Parse the response
            try:
                json_data = self._extract_json_from_text(response)
                return json_data
            except:
                # Fallback if JSON parsing fails
                return {
                    "rating": 5,
                    "confidence": 0.5,
                    "reasoning": "Unable to parse ChatGPT response",
                    "suggestions": ["Consider manual analysis"],
                }

        except Exception as e:
            self.logger.error(f"Error in ChatGPT trade opportunity analysis: {str(e)}")
            return {
                "rating": 5,
                "confidence": 0.5,
                "reasoning": f"Error: {str(e)}",
                "suggestions": ["System error occurred, consider manual analysis"],
            }

    def generate_trade_script(
        self,
        symbol: str,
        timeframe: str,
        data: pd.DataFrame,
        indicators: Dict,
        strategy_type: str,
    ) -> str:
        """
        Generate Pine Script trading strategy based on market data

        Args:
            symbol: The trading symbol
            timeframe: The trading timeframe
            data: OHLCV data
            indicators: Technical indicators
            strategy_type: Type of strategy to generate ('trend', 'reversal', 'breakout', etc.)

        Returns:
            Pine Script code as a string
        """
        try:
            if not self.api_key:
                return "// Error: OpenAI API key not configured"

            # Prepare market data
            self._prepare_market_context(
                symbol, timeframe, data, indicators
            )

            # Construct the prompt
            prompt = f"""
You are an expert Pine Script programmer for TradingView. Generate a complete Pine Script strategy based on the following:

Symbol: {symbol}
Timeframe: {timeframe}
Strategy Type: {strategy_type}

Technical Indicators:
{json.dumps(
               {k: str(v[
                                         -5:]) if isinstance(v,
                                         np.ndarray) else v for k,
                                         v in indicators.items()},
                                         indent=2)}
Create a complete Pine Script strategy that:
1. Uses relevant indicators for {strategy_type} strategy
2. Generates entry signals with proper risk management
3. Includes stop loss and take profit logic
4. Has appropriate position sizing
5. Includes useful comments explaining the strategy

Return ONLY the Pine Script code, properly formatted and ready to paste into TradingView.
"""

            # Get response from ChatGPT
            response = self._get_chatgpt_response(prompt)

            # Extract code blocks from response
            code = self._extract_code_from_text(response)
            return code

        except Exception as e:
            self.logger.error(f"Error generating Pine Script: {str(e)}")
            return f"// Error generating Pine Script: {str(e)}"

    def _prepare_market_context(
        self, symbol: str, timeframe: str, data: pd.DataFrame, indicators: Dict
    ) -> Dict:
        """Prepare market data summary for ChatGPT prompt"""
        try:
            # Get the last 5 rows of price data
            recent_data = data.tail(5).copy()
            recent_data.index = recent_data.index.astype(str)  # Convert index to string

            # Calculate basic market metrics
            close_prices = data["close"].values
            current_price = close_prices[-1]

            # Calculate volatility
            returns = np.diff(close_prices) / close_prices[:-1]
            volatility = np.std(returns) * 100  # as percentage

            # Determine trend direction
            sma20 = np.mean(close_prices[-20:])
            sma50 = (
                np.mean(close_prices[-50:])
                if len(close_prices) >= 50
                else np.mean(close_prices)
            )
            trend = (
                "uptrend"
                if current_price > sma20 > sma50
                else "downtrend" if current_price < sma20 < sma50 else "sideways"
            )

            # Process indicators
            processed_indicators = {}
            for key, value in indicators.items():
                if isinstance(value, np.ndarray):
                    # Only include the last 3 values for arrays
                    processed_indicators[key] = value[-3:].tolist()
                else:
                    processed_indicators[key] = value

            context = {
                "symbol": symbol,
                "timeframe": timeframe,
                "current_price": current_price,
                "daily_change_percent": (
                    ((close_prices[-1] / close_prices[-2]) - 1) * 100
                    if len(close_prices) > 1
                    else 0
                ),
                "weekly_change_percent": (
                    ((close_prices[-1] / close_prices[-7]) - 1) * 100
                    if len(close_prices) > 6
                    else 0
                ),
                "volatility_percent": volatility,
                "trend": trend,
                "key_indicators": processed_indicators,
                "recent_prices": recent_data[["open", "high", "low", "close"]].to_dict(
                    orient="records"
                ),
            }

            return context

        except Exception as e:
            self.logger.error(f"Error preparing market context: {str(e)}")
            return {"error": str(e)}

    def _prepare_news_summary(self, news_items: List[Dict]) -> str:
        """Prepare a summary of recent news"""
        if not news_items:
            return "No recent news available."

        summary = "Recent News:\n"

        for i, item in enumerate(news_items[:5]):  # Limit to 5 most recent news items
            summary += f"{i+1}. {item['title']}\n"
            summary += f" "
   Sentiment: {
                                              item.get(
                                                       'sentiment',
                                              'un + "known')},
                                              Impact: {item.get('impact',
                                              'u + "nknown')}\n"            summary += f"   {item.get('description', 'No description available.')[:100]}...\n\n"

        return summary

    def _construct_analysis_prompt(
        self, symbol: str, timeframe: str, market_context: Dict, news_summary: str
    ) -> str:
        """Construct a comprehensive prompt for market analysis"""
        return f"""
You are an expert financial market analyst with deep experience in technical and fundamental analysis.
Analyze the following market data and provide trading insights.

Symbol: {symbol}
Timeframe: {timeframe}

Market Context:
{json.dumps(market_context, indent=2)}

{news_summary}

Based on this information, provide:
1. A market sentiment analysis (bullish, bearish, or neutral)
2. Your confidence level in this sentiment (0.0-1.0)
3. Price targets for the next 24-48 hours (short-term)
4. Key support and resistance levels
5. Trading biases or potential setups
6. Risk factors to monitor

Format your response as JSON:
{{
  "sentiment": "bullish/bearish/neutral",
  "confidence": number,
  "price_targets": {{
    "short_term": {{
      "upper": number,
      "lower": number
    }},
    "support_levels": [numbers],
    "resistance_levels": [numbers]
  }},
  "trading_bias": "long/short/neutral",
  "reasoning": "string explanation",
  "key_indicators": ["string"],
  "risk_factors": ["string"],
  "recommendation": "string"
}}
"""

    def _get_chatgpt_response(self, prompt: str) -> str:
        """Get response from ChatGPT with retry logic"""
        for attempt in range(self.max_retries):
            try:
                response = openai.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "system",
                            "content": " "
You are a financial market analysis expe + "rt with deep experience in technical ana + "lysis, trading strategies, and market ps + "ychology.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    temperature=0.2,  # Lower temperature for more consistent, analytical responses
                    max_tokens=2000,
                )
                return response.choices[0].message.content

            except Exception as e:
                self.logger.warning(
                    f"ChatGPT API error (attempt {attempt+1}/{self.max_retries}): {str(e)}"
                )
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    raise

    def _parse_analysis_response(self, response: str) -> Dict:
        """Parse the JSON response from ChatGPT"""
        try:
            # Try to extract JSON from text
            json_data = self._extract_json_from_text(response)
            return json_data
        except Exception as e:
            self.logger.error(f"Error parsing ChatGPT response: {str(e)}")
            # Return a default response
            return {
                "sentiment": "neutral",
                "confidence": 0.5,
                "price_targets": {
                    "short_term": {"upper": None, "lower": None},
                    "support_levels": [],
                    "resistance_levels": [],
                },
                "trading_bias": "neutral",
                "reasoning": "Failed to parse ChatGPT response",
                "key_indicators": [],
                "risk_factors": ["System error in parsing response"],
                "recommendation": "Wait for system to stabilize",
            }

    def _extract_json_from_text(self, text: str) -> Dict:
        """Extract JSON object from text"""
        try:
            # Find JSON-like structure in the text
            start_idx = text.find("{")
            end_idx = text.rfind("}")

            if start_idx >= 0 and end_idx > start_idx:
                json_str = text[start_idx : end_idx + 1]
                return json.loads(json_str)
            else:
                raise ValueError("No JSON object found in the text")

        except Exception as e:
            self.logger.error(f"Error extracting JSON from text: {str(e)}")
            raise

    def _extract_code_from_text(self, text: str) -> str:
        """Extract code blocks from text"""
        start_markers = ["```pine", "```pinescript", "```"]
        end_marker = "```"

        for marker in start_markers:
            if marker in text:
                start_idx = text.find(marker) + len(marker)
                end_idx = text.find(end_marker, start_idx)

                if end_idx > start_idx:
                    code = text[start_idx:end_idx].strip()
                    return code

        # If no code block markers found, return the entire text
        return text

    def analyze_chart_patterns(self, symbol: str, data: pd.DataFrame) -> Dict:
        """Analyze chart patterns using ChatGPT"""
        try:
            if not self.api_key:
                return {"patterns": [], "confidence": 0}

            # Prepare data for pattern recognition
            recent_data = data.tail(50).copy()

            # Calculate key metrics
            highs = recent_data["high"].values
            lows = recent_data["low"].values
            closes = recent_data["close"].values

            # Prepare the prompt
            prompt = f"""
Analyze the following price data for {symbol} to identify chart patterns.
This is the historical price data (last 50 candles):

High prices: {highs.tolist()}
Low prices: {lows.tolist()}
Close prices: {closes.tolist()}

Identify any of the following chart patterns:
1. Head and Shoulders or Inverse Head and Shoulders
2. Double Top or Double Bottom
3. Triple Top or Triple Bottom
4. Rising or Falling Wedge
5. Ascending or Descending Triangle
6. Symmetrical Triangle
7. Bull or Bear Flag
8. Cup and Handle
9. Rounding Bottom or Top
10. Rectangle
11. Channel (Ascending, Descending, or Horizontal)
12. Island Reversal
13. Engulfing patterns
14. Morning/Evening Star
15. Doji patterns

For each identified pattern, provide:
1. The pattern name
2. Where it appears in the data (index positions)
3. Whether it's bullish or bearish
4. Confidence level (0.0-1.0)
5. Potential price targets based on the pattern

Format your response as JSON:
{{
  "patterns": [
    {{
      "name": "string",
      "position": [start_index, end_index],
      "bias": "bullish/bearish",
      "confidence": number,
      "target": number
    }}
  ],
  "overall_bias": "bullish/bearish/neutral",
  "confidence": number
}}
"""

            # Get response from ChatGPT
            response = self._get_chatgpt_response(prompt)

            # Parse the response
            try:
                json_data = self._extract_json_from_text(response)
                return json_data
            except:
                # Fallback if JSON parsing fails
                return {"patterns": [], "overall_bias": "neutral", "confidence": 0}

        except Exception as e:
            self.logger.error(f"Error in ChatGPT chart pattern analysis: {str(e)}")
            return {"patterns": [], "overall_bias": "neutral", "confidence": 0}


class DeepSeekerAnalyst:
    """DeepSeeker integration for more advanced market analysis"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.api_key = os.getenv("DEEPSEEKER_API_KEY")
        if not self.api_key:
            self.logger.warning(
                "DeepSeeker API key not found. DeepSeeker integration will not function."
            )
        self.cache = {}
        self.cache_duration = 60 * 30  # 30 minutes cache duration

    def analyze_market(
        self,
        symbol: str,
        timeframe: str,
        data: pd.DataFrame,
        news_items: List[Dict],
        indicators: Dict,
    ) -> Dict:
        """Analyze market using DeepSeeker (simulated for demo)"""
        # This is a placeholder for DeepSeeker integration
        # In a real implementation, you would connect to the DeepSeeker API

        # For now, we'll return a simulated response
        return {
            "sentiment": (
                "bullish"
                if data["close"].iloc[-1] > data["close"].iloc[-2]
                else "bearish"
            ),
            "confidence": 0.75,
            "recommendation": f" "
Consider {
                                                (
                                                 'long' if data['close'].iloc[ + "-1] > data['close'].iloc[-2] else 'short + "')} positions in {symbol}",
                                                            "reasoning": "DeepSeeker analysis based on price action and technical indicators",
        }


class AIMarketAnalyst:
    """Aggregates multiple AI analysis sources for comprehensive market insights"""

    def __init__(self):
        self.chatgpt = ChatGPTAnalyst()
        self.deepseeker = DeepSeekerAnalyst()
        self.logger = logging.getLogger(__name__)

    def get_comprehensive_analysis(
        self,
        symbol: str,
        timeframe: str,
        data: pd.DataFrame,
        news_items: List[Dict],
        indicators: Dict,
    ) -> Dict:
        """Get comprehensive analysis from multiple AI sources"""
        try:
            # Collect analyses from different sources
            chatgpt_analysis = self.chatgpt.analyze_market(
                symbol, timeframe, data, news_items, indicators
            )
            deepseeker_analysis = self.deepseeker.analyze_market(
                symbol, timeframe, data, news_items, indicators
            )

            # Add chart pattern recognition
            chart_patterns = self.chatgpt.analyze_chart_patterns(symbol, data)

            # Aggregate the analyses
            aggregated = {
                "symbol": symbol,
                "timeframe": timeframe,
                "timestamp": datetime.now().isoformat(),
                "price": data["close"].iloc[-1],
                "chatgpt_analysis": chatgpt_analysis,
                "deepseeker_analysis": deepseeker_analysis,
                "chart_patterns": chart_patterns,
                "consensus": {
                    "sentiment": self._get_consensus_sentiment(
                        chatgpt_analysis, deepseeker_analysis
                    ),
                    "confidence": self._get_consensus_confidence(
                        chatgpt_analysis, deepseeker_analysis, chart_patterns
                    ),
                    "trading_bias": self._get_consensus_bias(
                        chatgpt_analysis, deepseeker_analysis, chart_patterns
                    ),
                },
            }

            return aggregated

        except Exception as e:
            self.logger.error(f"Error in comprehensive market analysis: {str(e)}")
            return {
                "error": str(e),
                "symbol": symbol,
                "timeframe": timeframe,
                "timestamp": datetime.now().isoformat(),
            }

    def _get_consensus_sentiment(
        self, chatgpt_analysis: Dict, deepseeker_analysis: Dict
    ) -> str:
        """Get consensus sentiment from multiple sources"""
        chatgpt_sentiment = chatgpt_analysis.get("sentiment", "neutral")
        deepseeker_sentiment = deepseeker_analysis.get("sentiment", "neutral")

        # Simple voting mechanism
        if chatgpt_sentiment == deepseeker_sentiment:
            return chatgpt_sentiment

        # If conflicting, use the one with higher confidence
        chatgpt_confidence = chatgpt_analysis.get("confidence", 0.5)
        deepseeker_confidence = deepseeker_analysis.get("confidence", 0.5)

        return (
            chatgpt_sentiment
            if chatgpt_confidence > deepseeker_confidence
            else deepseeker_sentiment
        )

    def _get_consensus_confidence(
        self, chatgpt_analysis: Dict, deepseeker_analysis: Dict, chart_patterns: Dict
    ) -> float:
        """Get consensus confidence level"""
        confidences = [
            chatgpt_analysis.get("confidence", 0.5),
            deepseeker_analysis.get("confidence", 0.5),
        ]

        # Add chart pattern confidence if available
        pattern_confidence = chart_patterns.get("confidence", 0)
        if pattern_confidence > 0:
            confidences.append(pattern_confidence)

        # Calculate weighted average
        return sum(confidences) / len(confidences)

    def _get_consensus_bias(
        self, chatgpt_analysis: Dict, deepseeker_analysis: Dict, chart_patterns: Dict
    ) -> str:
        """Get consensus trading bias"""
        biases = []

        # ChatGPT bias
        chatgpt_bias = chatgpt_analysis.get("trading_bias", "neutral")
        biases.append((chatgpt_bias, chatgpt_analysis.get("confidence", 0.5)))

        # DeepSeeker bias (extracted from sentiment)
        deepseeker_sentiment = deepseeker_analysis.get("sentiment", "neutral")
        deepseeker_bias = (
            "long"
            if deepseeker_sentiment == "bullish"
            else "short" if deepseeker_sentiment == "bearish" else "neutral"
        )
        biases.append((deepseeker_bias, deepseeker_analysis.get("confidence", 0.5)))

        # Chart patterns bias
        chart_bias = chart_patterns.get("overall_bias", "neutral")
        chart_bias_mapped = (
            "long"
            if chart_bias == "bullish"
            else "short" if chart_bias == "bearish" else "neutral"
        )
        if chart_patterns.get("confidence", 0) > 0:
            biases.append((chart_bias_mapped, chart_patterns.get("confidence", 0.5)))

        # Calculate weighted bias
        long_weight = sum(conf for bias, conf in biases if bias == "long")
        short_weight = sum(conf for bias, conf in biases if bias == "short")
        neutral_weight = sum(conf for bias, conf in biases if bias == "neutral")

        if long_weight > short_weight and long_weight > neutral_weight:
            return "long"
        elif short_weight > long_weight and short_weight > neutral_weight:
            return "short"
        else:
            return "neutral"
