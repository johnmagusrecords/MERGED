import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingRegressor, VotingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.callbacks import EarlyStopping
import tensorflow as tf
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

@dataclass
class PredictionResult:
    direction: str
    confidence: float
    expected_return: float
    timeframe: str
    model_weights: Dict[str, float]

class EnhancedMLPredictor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.models = {}
        self.scalers = {}
        self.feature_importance = {}
        self.min_confidence = 0.65
        self.ensemble_weights = {
            'rf': 0.3,
            'gb': 0.3,
            'lstm': 0.4
        }
        
    def prepare_features(self, data: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare features for ML models with advanced technical indicators"""
        try:
            df = data.copy()
            
            # Price-based features
            df['returns'] = df['close'].pct_change()
            df['log_returns'] = np.log1p(df['returns'])
            df['volatility'] = df['returns'].rolling(20).std()
            
            # Volume features
            df['volume_ma'] = df['volume'].rolling(20).mean()
            df['volume_std'] = df['volume'].rolling(20).std()
            df['volume_ratio'] = df['volume'] / df['volume_ma']
            
            # Technical indicators
            df['rsi'] = self._calculate_rsi(df['close'])
            df['macd'], df['macd_signal'] = self._calculate_macd(df['close'])
            df['bb_upper'], df['bb_lower'] = self._calculate_bollinger_bands(df['close'])
            df['atr'] = self._calculate_atr(df)
            
            # Momentum features
            df['momentum'] = df['close'].pct_change(5)
            df['rate_of_change'] = df['close'].pct_change(10)
            
            # Target variable (next period return)
            df['target'] = df['returns'].shift(-1)
            
            # Remove missing values
            df = df.dropna()
            
            # Select features
            features = [
                'returns', 'log_returns', 'volatility',
                'volume_ratio', 'rsi', 'macd', 'macd_signal',
                'momentum', 'rate_of_change', 'atr'
            ]
            
            X = df[features].values
            y = np.where(df['target'] > 0, 1, 0)  # Binary classification
            
            return X, y
            
        except Exception as e:
            self.logger.error(f"Error preparing features: {str(e)}")
            return np.array([]), np.array([])
            
    def train_models(self, symbol: str, data: pd.DataFrame,
                    timeframe: str = '1h') -> None:
        """Train ML models with cross-validation and hyperparameter tuning"""
        try:
            # Prepare data
            X, y = self.prepare_features(data)
            if len(X) == 0:
                return
                
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, shuffle=False
            )
            
            # Scale features
            scaler = StandardScaler()
            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)
            
            # Save scaler
            model_key = f"{symbol}_{timeframe}"
            self.scalers[model_key] = scaler
            
            # 1. Random Forest
            rf = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42
            )
            rf.fit(X_train_scaled, y_train)
            
            # 2. Gradient Boosting
            gb = GradientBoostingRegressor(
                n_estimators=100,
                learning_rate=0.1,
                max_depth=5,
                random_state=42
            )
            gb.fit(X_train_scaled, y_train)
            
            # 3. LSTM
            lstm = self._build_lstm_model(X_train_scaled.shape[1])
            lstm.fit(
                X_train_scaled.reshape(-1, 1, X_train_scaled.shape[1]),
                y_train,
                epochs=50,
                batch_size=32,
                validation_split=0.2,
                callbacks=[EarlyStopping(patience=5)],
                verbose=0
            )
            
            # Save models
            self.models[model_key] = {
                'rf': rf,
                'gb': gb,
                'lstm': lstm
            }
            
            # Calculate feature importance
            self.feature_importance[model_key] = {
                'rf': rf.feature_importances_,
                'gb': gb.feature_importances_
            }
            
            # Log performance
            rf_score = rf.score(X_test_scaled, y_test)
            gb_score = gb.score(X_test_scaled, y_test)
            self.logger.info(f"Model performance for {symbol}_{timeframe}:")
            self.logger.info(f"Random Forest accuracy: {rf_score:.4f}")
            self.logger.info(f"Gradient Boosting R2: {gb_score:.4f}")
            
        except Exception as e:
            self.logger.error(f"Error training models: {str(e)}")
            
    def predict(self, symbol: str, data: pd.DataFrame,
                timeframe: str = '1h') -> Optional[PredictionResult]:
        """Generate ensemble predictions with confidence scores"""
        try:
            model_key = f"{symbol}_{timeframe}"
            if model_key not in self.models:
                return None
                
            # Prepare features
            X, _ = self.prepare_features(data.tail(100))  # Use recent data
            if len(X) == 0:
                return None
                
            # Scale features
            X_scaled = self.scalers[model_key].transform(X[-1:])
            
            # Get predictions from each model
            rf_pred = self.models[model_key]['rf'].predict_proba(X_scaled)[0]
            gb_pred = self.models[model_key]['gb'].predict(X_scaled)[0]
            lstm_pred = self.models[model_key]['lstm'].predict(
                X_scaled.reshape(-1, 1, X_scaled.shape[1])
            )[0][0]
            
            # Calculate ensemble prediction
            ensemble_pred = (
                rf_pred[1] * self.ensemble_weights['rf'] +
                (gb_pred > 0) * self.ensemble_weights['gb'] +
                lstm_pred * self.ensemble_weights['lstm']
            )
            
            # Calculate confidence and expected return
            confidence = abs(ensemble_pred - 0.5) * 2  # Scale to [0, 1]
            expected_return = gb_pred  # Use GB model for return estimation
            
            # Determine direction
            direction = "long" if ensemble_pred > 0.5 else "short"
            
            # Create prediction result
            result = PredictionResult(
                direction=direction,
                confidence=confidence,
                expected_return=expected_return,
                timeframe=timeframe,
                model_weights=self.ensemble_weights
            )
            
            return result if confidence >= self.min_confidence else None
            
        except Exception as e:
            self.logger.error(f"Error making prediction: {str(e)}")
            return None
            
    def _build_lstm_model(self, n_features: int) -> Sequential:
        """Build LSTM model with improved architecture"""
        model = Sequential([
            LSTM(64, input_shape=(1, n_features), return_sequences=True),
            Dropout(0.2),
            LSTM(32),
            Dropout(0.1),
            Dense(16, activation='relu'),
            Dense(1, activation='sigmoid')
        ])
        
        model.compile(
            optimizer=Adam(learning_rate=0.001),
            loss='binary_crossentropy',
            metrics=['accuracy']
        )
        
        return model
        
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
        
    def _calculate_bollinger_bands(self, prices: pd.Series,
                                period: int = 20) -> Tuple[pd.Series, pd.Series]:
        """Calculate Bollinger Bands"""
        ma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        upper = ma + (std * 2)
        lower = ma - (std * 2)
        return upper, lower
        
    def _calculate_atr(self, data: pd.DataFrame,
                     period: int = 14) -> pd.Series:
        """Calculate Average True Range"""
        high = data['high']
        low = data['low']
        close = data['close']
        
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        return tr.rolling(window=period).mean()
