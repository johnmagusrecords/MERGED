import os
import time
import logging
from datetime import datetime, timedelta
from enhanced_trading_engine import EnhancedTradingEngine
from risk_manager import EnhancedRiskManager
from ml_predictor import EnhancedMLPredictor
from market_regime import EnhancedMarketRegimeDetector
from news_analyzer import NewsAnalyzer
import pandas as pd
import numpy as np

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extended_test():
    try:
        # Initialize components
        engine = EnhancedTradingEngine()
        risk_manager = EnhancedRiskManager()
        ml_predictor = EnhancedMLPredictor()
        regime_detector = EnhancedMarketRegimeDetector()
        news_analyzer = NewsAnalyzer()

        # Extended symbol list
        symbols = ['BTCUSD', 'ETHUSD', 'US100', 'EURUSD', 'GBPUSD', 'USDJPY', 'XAUUSD', 'US500']
        timeframes = ['1h', '4h', '1d']

        # Generate extended market data
        for symbol in symbols:
            engine.market_data[symbol] = {}
            for timeframe in timeframes:
                # Generate sample OHLCV data with trends and volatility
                periods = 1000
                dates = pd.date_range(end=datetime.now(), periods=periods, freq='h')
                
                # Create trending data with random walks
                trend = np.cumsum(np.random.normal(0.0001, 0.001, periods))
                volatility = np.abs(np.random.normal(0, 0.002, periods))
                
                close = 100 * (1 + trend)
                data = pd.DataFrame({
                    'open': close * (1 + np.random.normal(0, volatility)),
                    'high': close * (1 + np.abs(np.random.normal(0, volatility))),
                    'low': close * (1 - np.abs(np.random.normal(0, volatility))),
                    'close': close,
                    'volume': np.random.normal(1000, 100, periods) * (1 + np.abs(trend))
                }, index=dates)
                
                engine.market_data[symbol][timeframe] = data

        # Run extended tests
        for symbol in symbols:
            logger.info(f"\n=== Testing {symbol} ===")

            # Train ML models with extended data
            ml_predictor.train_models(symbol, engine.market_data[symbol]['1h'])

            # Test multiple timeframes
            for timeframe in timeframes:
                logger.info(f"\nTimeframe: {timeframe}")
                
                # Market regime analysis
                regime, confidence = regime_detector.detect_regime(symbol, engine.market_data[symbol][timeframe])
                logger.info(f"Market Regime: {regime.value} (confidence: {confidence:.2f})")

                # News impact
                should_pause, reason = news_analyzer.should_pause_trading(symbol)
                logger.info(f"News Analysis - Should pause: {should_pause}, Reason: {reason}")

                # ML predictions
                prediction = ml_predictor.predict(symbol, engine.market_data[symbol][timeframe])
                if prediction:
                    logger.info(f"ML Prediction - Direction: {prediction.direction}, Confidence: {prediction.confidence:.2f}, Expected Return: {prediction.expected_return:.2f}%")
                else:
                    logger.info("No ML prediction available")

                # Risk calculations
                position_size = risk_manager.calculate_position_size(
                    symbol=symbol,
                    entry_price=engine.market_data[symbol][timeframe]['close'].iloc[-1],
                    stop_loss=engine.market_data[symbol][timeframe]['low'].iloc[-1],
                    account_balance=100000.0,
                    historical_data=engine.market_data[symbol][timeframe]
                )
                logger.info(f"Position Size: {position_size:.2f}")

                # Trading signals
                signal, params = engine.analyze_market(symbol)
                logger.info(f"Trading Signal: {signal}")
                if params:
                    logger.info(f"Trade Parameters: Entry={params['entry_price']:.2f}, SL={params['stop_loss']:.2f}, TP={params['take_profit']:.2f}")

        logger.info("\nAll extended tests completed successfully!")

    except Exception as e:
        logger.error(f"Error in extended test: {str(e)}")
        raise

if __name__ == "__main__":
    extended_test()
