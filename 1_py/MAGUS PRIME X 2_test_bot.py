import logging
from datetime import datetime

import numpy as np
import pandas as pd

from enhanced_trading_engine import EnhancedTradingEngine
from market_regime import EnhancedMarketRegimeDetector
from ml_predictor import EnhancedMLPredictor
from news_analyzer import NewsAnalyzer
from risk_manager import EnhancedRiskManager

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_bot():
    try:
        # Initialize components
        engine = EnhancedTradingEngine()
        risk_manager = EnhancedRiskManager()
        ml_predictor = EnhancedMLPredictor()
        regime_detector = EnhancedMarketRegimeDetector()
        news_analyzer = NewsAnalyzer()

        # Test symbols
        symbols = ["BTCUSD", "ETHUSD", "US100"]
        timeframes = ["1h", "4h"]

        # Generate sample market data
        for symbol in symbols:
            engine.market_data[symbol] = {}
            for timeframe in timeframes:
                # Generate sample OHLCV data
                periods = 500
                dates = pd.date_range(end=datetime.now(), periods=periods, freq="h")
                data = pd.DataFrame(
                    {
                        "open": np.random.normal(100, 10, periods),
                        "high": np.random.normal(105, 10, periods),
                        "low": np.random.normal(95, 10, periods),
                        "close": np.random.normal(100, 10, periods),
                        "volume": np.random.normal(1000, 100, periods),
                    },
                    index=dates,
                )

                # Ensure high is highest and low is lowest
                data["high"] = data[["open", "high", "close"]].max(axis=1)
                data["low"] = data[["open", "low", "close"]].min(axis=1)

                engine.market_data[symbol][timeframe] = data

        # Test each symbol
        for symbol in symbols:
            logger.info(f"Testing {symbol}...")

            # Train ML models
            ml_predictor.train_models(symbol, engine.market_data[symbol]["1h"])

            # Test market regime detection
            regime, confidence = regime_detector.detect_regime(
                symbol, engine.market_data[symbol]["1h"]
            )
            logger.info(f"Market Regime: {regime.value} (confidence: {confidence:.2f})")

            # Test news analysis
            should_pause, reason = news_analyzer.should_pause_trading(symbol)
            logger.info(
                f"News Analysis - Should pause: {should_pause}, Reason: {reason}"
            )

            # Test ML prediction
            prediction = ml_predictor.predict(symbol, engine.market_data[symbol]["1h"])
            if prediction:
                logger.info(
                    f" "
ML Prediction - Direction: {
                                                        prediction.d + "irection},
                                                        Confidence: {prediction.confi + "dence:.2f},
                                                        Expected Return: {prediction + ".expected_return:.2f}%"                )
            else:
                logger.info("No ML prediction available (confidence below threshold)")

            # Test risk management
            position_size = risk_manager.calculate_position_size(
                symbol=symbol,
                entry_price=engine.market_data[symbol]["1h"]["close"].iloc[-1],
                stop_loss=engine.market_data[symbol]["1h"]["low"].iloc[-1],
                account_balance=10000.0,
                historical_data=engine.market_data[symbol]["1h"],
            )
            logger.info(f"Position Size: {position_size:.2f}")

            # Test trading signal generation
            signal, params = engine.analyze_market(symbol)
            logger.info(f"Trading Signal: {signal}")
            if params:
                logger.info(
                    f" "
Trade Parameters: Entry={
                                                     params[
                                                            'entry_p + "rice']:.2f},
                                                     SL={params['stop_loss']:.2f + "},
                                                     TP={params['take_profit']:.2f}"                )

        logger.info("All tests completed successfully!")

    except Exception as e:
        logger.error(f"Error in test_bot: {str(e)}")
        raise


if __name__ == "__main__":
    test_bot()
