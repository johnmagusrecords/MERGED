import logging
import os
from datetime import datetime
from typing import Dict, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.models import Sequential
from tensorflow.keras.optimizers import Adam


class AIPredictor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.model = None
        self.scaler = StandardScaler()
        self.lookback = 20  # Number of periods to look back
        self.feature_columns = [
            "open",
            "high",
            "low",
            "close",
            "volume",
            "rsi",
            "macd",
            "signal",
            "upper_bb",
            "lower_bb",
        ]
        self.model_cache = {}
        self.prediction_cache = {}
        self.cache_ttl = 300  # 5 minutes

    def _create_model(self, input_shape: Tuple) -> Sequential:
        """Create and compile the LSTM model"""
        model = Sequential(
            [
                LSTM(100, return_sequences=True, input_shape=input_shape),
                Dropout(0.2),
                LSTM(50, return_sequences=False),
                Dropout(0.2),
                Dense(25, activation="relu"),
                Dense(1, activation="sigmoid"),
            ]
        )

        model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss="binary_crossentropy",
            metrics=["accuracy"],
        )

        return model

    def _prepare_data(self, data: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare data for LSTM model"""
        # Calculate technical indicators
        data["rsi"] = self._calculate_rsi(data["close"])
        macd, signal = self._calculate_macd(data["close"])
        data["macd"] = macd
        data["signal"] = signal
        upper, lower = self._calculate_bollinger_bands(data["close"])
        data["upper_bb"] = upper
        data["lower_bb"] = lower

        # Create features
        features = data[self.feature_columns].values
        features = self.scaler.fit_transform(features)

        # Create sequences
        X, y = [], []
        for i in range(self.lookback, len(features)):
            X.append(features[i - self.lookback : i])
            # Create target: 1 if price goes up, 0 if down
            y.append(1 if data["close"].iloc[i] > data["close"].iloc[i - 1] else 0)

        return np.array(X), np.array(y)

    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI indicator"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def _calculate_macd(self, prices: pd.Series) -> Tuple[pd.Series, pd.Series]:
        """Calculate MACD indicator"""
        exp1 = prices.ewm(span=12, adjust=False).mean()
        exp2 = prices.ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9, adjust=False).mean()
        return macd, signal

    def _calculate_bollinger_bands(
        self, prices: pd.Series, period: int = 20
    ) -> Tuple[pd.Series, pd.Series]:
        """Calculate Bollinger Bands"""
        sma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        upper_band = sma + (std * 2)
        lower_band = sma - (std * 2)
        return upper_band, lower_band

    def train(self, symbol: str, data: pd.DataFrame) -> None:
        """Train the model on historical data"""
        try:
            X, y = self._prepare_data(data)

            if len(X) < self.lookback:
                self.logger.warning(f"Not enough data to train model for {symbol}")
                return

            # Create and train model
            self.model = self._create_model((self.lookback, len(self.feature_columns)))
            self.model.fit(
                X, y, epochs=50, batch_size=32, validation_split=0.2, verbose=0
            )

            # Save model
            model_path = f"models/{symbol}_model.h5"
            scaler_path = f"models/{symbol}_scaler.pkl"

            os.makedirs("models", exist_ok=True)
            self.model.save(model_path)
            joblib.dump(self.scaler, scaler_path)

            self.logger.info(f"Model trained and saved for {symbol}")

        except Exception as e:
            self.logger.error(f"Error training model for {symbol}: {str(e)}")

    def predict(self, symbol: str, data: pd.DataFrame) -> Dict:
        """Make price movement predictions"""
        try:
            # Check cache
            cache_key = f"{symbol}_{datetime.now().strftime('%Y%m%d%H%M')}"
            if cache_key in self.prediction_cache:
                return self.prediction_cache[cache_key]

            # Load model if not loaded
            if symbol not in self.model_cache:
                model_path = f"models/{symbol}_model.h5"
                scaler_path = f"models/{symbol}_scaler.pkl"

                if not os.path.exists(model_path):
                    self.logger.warning(f"No trained model found for {symbol}")
                    return {
                        "probability": 0.5,
                        "confidence": 0.0,
                        "direction": "neutral",
                    }

                self.model = Sequential.load_model(model_path)
                self.scaler = joblib.load(scaler_path)
                self.model_cache[symbol] = {
                    "model": self.model,
                    "scaler": self.scaler,
                    "loaded_at": datetime.now(),
                }

            # Prepare latest data
            X, _ = self._prepare_data(data.tail(self.lookback + 1))
            if len(X) < 1:
                return {"probability": 0.5, "confidence": 0.0, "direction": "neutral"}

            # Make prediction
            prediction = self.model.predict(X[-1:], verbose=0)[0][0]

            # Calculate confidence based on prediction probability
            confidence = abs(prediction - 0.5) * 2  # Scale to 0-1

            result = {
                "probability": float(prediction),
                "confidence": float(confidence),
                "direction": "buy" if prediction > 0.5 else "sell",
            }

            # Cache prediction
            self.prediction_cache[cache_key] = result

            return result

        except Exception as e:
            self.logger.error(f"Error making prediction for {symbol}: {str(e)}")
            return {"probability": 0.5, "confidence": 0.0, "direction": "neutral"}

    def get_model_metrics(self, symbol: str) -> Dict:
        """Get model performance metrics"""
        try:
            model_path = f"models/{symbol}_model.h5"
            if not os.path.exists(model_path):
                return {"accuracy": 0, "last_trained": None}

            model_stats = os.stat(model_path)
            last_trained = datetime.fromtimestamp(model_stats.st_mtime)

            # Load model history if available
            history_path = f"models/{symbol}_history.pkl"
            if os.path.exists(history_path):
                history = joblib.load(history_path)
                accuracy = (
                    history.get("accuracy", [])[-1] if history.get("accuracy") else 0
                )
            else:
                accuracy = 0

            return {"accuracy": accuracy, "last_trained": last_trained.isoformat()}

        except Exception as e:
            self.logger.error(f"Error getting model metrics for {symbol}: {str(e)}")
            return {"accuracy": 0, "last_trained": None}

    def cleanup_cache(self):
        """Clean up expired cache entries"""
        current_time = datetime.now()

        # Clean prediction cache
        expired_predictions = [
            key
            for key in self.prediction_cache.keys()
            if (
                current_time - datetime.strptime(key.split("_")[1], "%Y%m%d%H%M")
            ).seconds
            > self.cache_ttl
        ]
        for key in expired_predictions:
            del self.prediction_cache[key]

        # Clean model cache
        expired_models = [
            symbol
            for symbol, data in self.model_cache.items()
            if (current_time - data["loaded_at"]).seconds
            > 3600  # 1 hour TTL for models
        ]
        for symbol in expired_models:
            del self.model_cache[symbol]
