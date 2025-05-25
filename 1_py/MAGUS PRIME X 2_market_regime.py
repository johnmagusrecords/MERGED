import logging
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Tuple

import numpy as np
import pandas as pd
from hmmlearn import hmm
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


class MarketRegime(Enum):
    TRENDING_UP = "trending_up"
    TRENDING_DOWN = "trending_down"
    RANGING = "ranging"
    BREAKOUT = "breakout"
    REVERSAL = "reversal"
    HIGH_VOLATILITY = "high_volatility"
    LOW_VOLATILITY = "low_volatility"


@dataclass
class RegimeAnalysis:
    regime: MarketRegime
    confidence: float
    volatility: float
    momentum: float
    trend_strength: float
    support_resistance: Dict[str, float]
    indicators: Dict[str, float]


class EnhancedMarketRegimeDetector:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.scaler = StandardScaler()
        self.hmm_model = None
        self.kmeans_model = None
        self.min_confidence = 0.6
        self.lookback_periods = {"short": 20, "medium": 50, "long": 200}

    def detect_regime(
        self, symbol: str, data: pd.DataFrame
    ) -> Tuple[MarketRegime, float]:
        """Detect market regime using multiple techniques"""
        try:
            # Train models if not trained
            if self.hmm_model is None or self.kmeans_model is None:
                self.train_models(data)

            # Prepare features
            features = self._prepare_regime_features(data)
            if len(features) == 0:
                return MarketRegime.RANGING, 0.0

            # Scale features
            scaled_features = self.scaler.transform(features)

            # Get predictions from both models
            hmm_state = self.hmm_model.predict(scaled_features)[-1]
            kmeans_cluster = self.kmeans_model.predict(scaled_features)[-1]

            # Calculate trend strength
            trend_strength = self._calculate_trend_strength(data)

            # Calculate volatility
            volatility = self._calculate_volatility(data)

            # Determine regime based on combined analysis
            regime, confidence = self._determine_regime(
                hmm_state, kmeans_cluster, trend_strength, volatility, data
            )

            return regime, confidence

        except Exception as e:
            self.logger.error(f"Error detecting regime: {str(e)}")
            return MarketRegime.RANGING, 0.0

    def train_models(self, data: pd.DataFrame) -> None:
        """Train HMM and K-means models for regime detection"""
        try:
            # Prepare features for training
            features = self._prepare_regime_features(data)
            if len(features) == 0:
                return

            # Scale features
            scaled_features = self.scaler.fit_transform(features)

            # Train HMM
            self.hmm_model = hmm.GaussianHMM(n_components=5, random_state=42)
            self.hmm_model.fit(scaled_features)

            # Train K-means
            self.kmeans_model = KMeans(n_clusters=5, random_state=42)
            self.kmeans_model.fit(scaled_features)

        except Exception as e:
            self.logger.error(f"Error training models: {str(e)}")

    def _prepare_regime_features(self, data: pd.DataFrame) -> np.ndarray:
        """Prepare features for regime detection"""
        try:
            if len(data) < self.lookback_periods["long"]:
                return np.array([])

            df = data.copy()

            # Price features
            df["returns"] = df["close"].pct_change()
            df["log_returns"] = np.log1p(df["returns"])

            # Moving averages
            for period in self.lookback_periods.values():
                df[f"sma_{period}"] = df["close"].rolling(window=period).mean()
                df[f"std_{period}"] = df["returns"].rolling(window=period).std()

            # Momentum indicators
            df["rsi"] = self._calculate_rsi(df["close"])
            df["momentum"] = df["close"] / df["close"].shift(20) - 1

            # Volatility indicators
            df["atr"] = self._calculate_atr(df)
            df["bb_width"] = self._calculate_bollinger_width(df["close"])

            # Volume features
            if "volume" in df.columns:
                df["volume_ma"] = df["volume"].rolling(window=20).mean()
                df["volume_std"] = df["volume"].rolling(window=20).std()

            # Drop NaN values
            df = df.dropna()

            feature_columns = [
                "returns",
                "log_returns",
                "sma_20",
                "sma_50",
                "sma_200",
                "std_20",
                "std_50",
                "std_200",
                "rsi",
                "momentum",
                "atr",
                "bb_width",
            ]

            if "volume" in df.columns:
                feature_columns.extend(["volume_ma", "volume_std"])

            return df[feature_columns].values

        except Exception as e:
            self.logger.error(f"Error preparing features: {str(e)}")
            return np.array([])

    def _calculate_trend_strength(self, data: pd.DataFrame) -> float:
        """Calculate trend strength using multiple indicators"""
        try:
            # Calculate moving averages
            sma_20 = data["close"].rolling(window=20).mean()
            sma_50 = data["close"].rolling(window=50).mean()
            sma_200 = data["close"].rolling(window=200).mean()

            # Calculate directional strength
            price = data["close"].iloc[-1]
            trend_signals = [
                price > sma_20.iloc[-1],
                sma_20.iloc[-1] > sma_50.iloc[-1],
                sma_50.iloc[-1] > sma_200.iloc[-1],
                price > data["close"].rolling(window=10).mean().iloc[-1],
            ]

            # Calculate momentum
            momentum = self._calculate_momentum(data)

            # Combine signals
            trend_strength = (sum(trend_signals) / len(trend_signals) + momentum) / 2

            return trend_strength

        except Exception as e:
            self.logger.error(f"Error calculating trend strength: {str(e)}")
            return 0.5

    def _calculate_volatility(self, data: pd.DataFrame) -> float:
        """Calculate market volatility"""
        try:
            returns = data["close"].pct_change()
            recent_vol = returns.tail(20).std()
            historical_vol = returns.std()

            # Normalize volatility
            normalized_vol = recent_vol / historical_vol if historical_vol != 0 else 1.0

            return normalized_vol

        except Exception as e:
            self.logger.error(f"Error calculating volatility: {str(e)}")
            return 1.0

    def _determine_regime(
        self,
        hmm_state: int,
        kmeans_cluster: int,
        trend_strength: float,
        volatility: float,
        data: pd.DataFrame,
    ) -> Tuple[MarketRegime, float]:
        """Determine market regime based on multiple factors"""
        try:
            # Get recent price action
            recent_returns = data["close"].pct_change().tail(20)
            price_direction = np.mean(recent_returns)

            # Calculate confidence based on model agreement
            model_agreement = hmm_state == kmeans_cluster
            base_confidence = 0.6 if model_agreement else 0.4

            # Adjust confidence based on trend strength and volatility
            confidence = base_confidence * (0.5 + trend_strength * 0.5)

            # Determine regime
            if volatility > 2.0:
                regime = MarketRegime.HIGH_VOLATILITY
                confidence = min(confidence * 1.2, 1.0)
            elif volatility < 0.5:
                regime = MarketRegime.LOW_VOLATILITY
                confidence = min(confidence * 1.1, 1.0)
            elif trend_strength > 0.7:
                regime = (
                    MarketRegime.TRENDING_UP
                    if price_direction > 0
                    else MarketRegime.TRENDING_DOWN
                )
                confidence = min(confidence * trend_strength, 1.0)
            elif self._detect_breakout(data):
                regime = MarketRegime.BREAKOUT
                confidence = min(confidence * 1.1, 1.0)
            elif self._detect_reversal(data):
                regime = MarketRegime.REVERSAL
                confidence = min(
                    confidence * 0.9, 1.0
                )  # Lower confidence for reversals
            else:
                regime = MarketRegime.RANGING
                confidence = min(
                    confidence * 0.8, 1.0
                )  # Lower confidence for ranging markets

            return regime, confidence

        except Exception as e:
            self.logger.error(f"Error determining regime: {str(e)}")
            return MarketRegime.RANGING, 0.0

    def _detect_breakout(self, data: pd.DataFrame) -> bool:
        """Detect potential breakout patterns"""
        try:
            # Calculate Bollinger Bands
            std = data["close"].rolling(window=20).std()
            middle = data["close"].rolling(window=20).mean()
            upper = middle + (std * 2)
            lower = middle - (std * 2)

            # Get recent prices
            recent_close = data["close"].iloc[-1]
            prev_close = data["close"].iloc[-2]

            # Check for breakout conditions
            upper_breakout = (
                prev_close <= upper.iloc[-2] and recent_close > upper.iloc[-1]
            )
            lower_breakout = (
                prev_close >= lower.iloc[-2] and recent_close < lower.iloc[-1]
            )

            # Check volume if available
            volume_confirmation = True
            if "volume" in data.columns:
                recent_volume = data["volume"].iloc[-1]
                avg_volume = data["volume"].rolling(window=20).mean().iloc[-1]
                volume_confirmation = recent_volume > avg_volume * 1.5

            return (upper_breakout or lower_breakout) and volume_confirmation

        except Exception as e:
            self.logger.error(f"Error detecting breakout: {str(e)}")
            return False

    def _detect_reversal(self, data: pd.DataFrame) -> bool:
        """Detect potential reversal patterns"""
        try:
            # Calculate RSI
            rsi = self._calculate_rsi(data["close"])

            # Calculate recent price action
            returns = data["close"].pct_change()
            recent_trend = np.sum(returns.tail(10))

            # Check for reversal conditions
            overbought = rsi.iloc[-1] > 70 and recent_trend > 0
            oversold = rsi.iloc[-1] < 30 and recent_trend < 0

            # Check for candlestick patterns if available
            pattern_confirmation = self._check_reversal_patterns(data)

            return (overbought or oversold) and pattern_confirmation

        except Exception as e:
            self.logger.error(f"Error detecting reversal: {str(e)}")
            return False

    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index"""
        try:
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))

            return rsi

        except Exception as e:
            self.logger.error(f"Error calculating RSI: {str(e)}")
            return pd.Series(index=prices.index)

    def _calculate_atr(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Average True Range"""
        try:
            high = data["high"]
            low = data["low"]
            close = data["close"]

            tr1 = high - low
            tr2 = abs(high - close.shift())
            tr3 = abs(low - close.shift())

            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            atr = tr.rolling(window=period).mean()

            return atr

        except Exception as e:
            self.logger.error(f"Error calculating ATR: {str(e)}")
            return pd.Series(index=data.index)

    def _calculate_bollinger_width(
        self, prices: pd.Series, period: int = 20, num_std: float = 2.0
    ) -> pd.Series:
        """Calculate Bollinger Bands width"""
        try:
            middle = prices.rolling(window=period).mean()
            std = prices.rolling(window=period).std()

            upper = middle + (std * num_std)
            lower = middle - (std * num_std)

            width = (upper - lower) / middle
            return width

        except Exception as e:
            self.logger.error(f"Error calculating Bollinger width: {str(e)}")
            return pd.Series(index=prices.index)

    def _calculate_momentum(self, data: pd.DataFrame, period: int = 10) -> float:
        """Calculate price momentum"""
        try:
            close = data["close"]
            momentum = close.iloc[-1] / close.iloc[-period] - 1

            # Normalize momentum to [-1, 1]
            return np.tanh(momentum)

        except Exception as e:
            self.logger.error(f"Error calculating momentum: {str(e)}")
            return 0.0

    def _check_reversal_patterns(self, data: pd.DataFrame) -> bool:
        """Check for candlestick reversal patterns"""
        try:
            # Get recent candles
            open_prices = data["open"].tail(3)
            close_prices = data["close"].tail(3)
            high_prices = data["high"].tail(3)
            low_prices = data["low"].tail(3)

            # Check for engulfing pattern
            bullish_engulfing = (
                close_prices.iloc[-2] < open_prices.iloc[-2]  # Previous red candle
                and close_prices.iloc[-1] > open_prices.iloc[-1]  # Current green candle
                and open_prices.iloc[-1]
                < close_prices.iloc[-2]  # Opens below previous close
                and close_prices.iloc[-1]
                > open_prices.iloc[-2]  # Closes above previous open
            )

            bearish_engulfing = (
                close_prices.iloc[-2] > open_prices.iloc[-2]  # Previous green candle
                and close_prices.iloc[-1] < open_prices.iloc[-1]  # Current red candle
                and open_prices.iloc[-1]
                > close_prices.iloc[-2]  # Opens above previous close
                and close_prices.iloc[-1]
                < open_prices.iloc[-2]  # Closes below previous open
            )

            # Check for doji
            doji = (
                abs(close_prices.iloc[-1] - open_prices.iloc[-1])
                <= (high_prices.iloc[-1] - low_prices.iloc[-1]) * 0.1
            )

            return bullish_engulfing or bearish_engulfing or doji

        except Exception as e:
            self.logger.error(f"Error checking reversal patterns: {str(e)}")
            return False
