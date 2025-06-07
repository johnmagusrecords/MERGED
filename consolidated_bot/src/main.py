"""Entry point for the consolidated trading bot."""

from .strategy import Strategy
from .trading import TradingEngine


def main():
    strategy = Strategy()
    engine = TradingEngine(strategy)
    engine.run()


if __name__ == "__main__":
    main()
