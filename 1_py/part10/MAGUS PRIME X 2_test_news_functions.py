import logging

from news_monitor import (
    check_news_for_asset,
    get_market_sentiment,
    news_monitor,
    simple_check_market_status,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def test_news_functions():
    """Test the enhanced news monitoring functions"""
    print("===== TESTING ENHANCED NEWS MONITORING =====")

    # Test assets
    test_assets = ["BTCUSD", "GOLD", "EURUSD", "US30", "GER40"]

    # Test simple functions
    print("\n1. Testing simple news retrieval:")
    print("-" * 50)

    for asset in test_assets[:2]:  # Just test a couple assets
        print(f"\nNews for {asset}:")
        headlines = check_news_for_asset(asset)

        if headlines:
            for i, headline in enumerate(headlines, 1):
                print(f"{i}. {headline}")
        else:
            print("No news found")

    # Test sentiment analysis
    print("\n\n2. Testing sentiment analysis:")
    print("-" * 50)

    for asset in test_assets[:2]:  # Just test a couple assets
        print(f"\nSentiment for {asset}:")
        sentiment = get_market_sentiment(asset)

        print(f"Message: {sentiment.get('message', 'Not available')}")
        print(f"Score: {sentiment.get('score', 0):.2f}")

        if sentiment.get("news"):
            print("Top headlines affecting sentiment:")
            for article in sentiment["news"][:2]:  # Show just 2 articles
                print(f"- {article['title']}")

    # Test market status checks
    print("\n\n3. Testing market status checker:")
    print("-" * 50)

    for asset in test_assets:
        status = "OPEN" if simple_check_market_status(asset) else "CLOSED"
        print(f"{asset}: {status}")

    # Test the news monitor itself
    print("\n\n4. News monitor status:")
    print("-" * 50)

    if hasattr(news_monitor, "enabled"):
        print(f"News monitoring enabled: {news_monitor.enabled}")
        print(
            f"Alpha Vantage Key available: {'Yes' if news_monitor.alpha_vantage_key else 'No'}"
        )
        print(f"NewsAPI client available: {'Yes' if news_monitor.newsapi else 'No'}")
        print(f"Asset keywords configured: {len(news_monitor.asset_keywords)} assets")


if __name__ == "__main__":
    test_news_functions()
    print("\nTest complete. Press Enter to exit...")
    input()
