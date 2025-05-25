import logging

from send_signal_helper import ASSET_CONFIG, send_signal

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def test_config_loading():
    """Test if asset configuration was loaded properly"""
    logger.info("Testing asset configuration loading")

    if not ASSET_CONFIG:
        logger.warning("No asset configuration loaded")
    else:
        logger.info(f"Successfully loaded {len(ASSET_CONFIG)} assets")

        # Display first few assets as a sample
        logger.info("Sample asset configurations:")
        for i, (symbol, config) in enumerate(ASSET_CONFIG.items()):
            logger.info(f"{symbol}: {config}")
            if i >= 2:  # Show only first 3 assets
                break


def test_send_configured_signal():
    """Test sending a signal for an asset in the configuration"""
    logger.info("Testing signal for configured asset (GOLD)")

    response = send_signal(
        pair="GOLD",  # This should be in the config
        entry=3110.50,
        stop_loss=3095.75,
        tp1=3125.25,
    )

    logger.info(f"Response: {response}")

    # The signal should include metadata from the config
    logger.info("The signal should have included:")
    if "GOLD" in ASSET_CONFIG:
        logger.info(f"Asset Type: {ASSET_CONFIG['GOLD'].get('type')}")
        logger.info(f"Strategy: {ASSET_CONFIG['GOLD'].get('strategy')}")
        logger.info(f"Default Timeframe: {ASSET_CONFIG['GOLD'].get('timeframe')}")
        logger.info(f"Hold Hours: {ASSET_CONFIG['GOLD'].get('hold_hours')}")


def test_send_unconfigured_signal():
    """Test sending a signal for an asset not in the configuration"""
    logger.info("Testing signal for unconfigured asset (UNKNOWN)")

    response = send_signal(
        pair="UNKNOWN",  # Not in config, should use defaults
        entry=100.50,
        stop_loss=99.75,
        tp1=101.25,
        timeframe="5m",  # Explicitly set timeframe
    )

    logger.info(f"Response: {response}")
    logger.info(
        "The signal should have used default values for category, strategy, etc."
    )


if __name__ == "__main__":
    logger.info("===== TESTING ENHANCED SIGNAL CAPABILITIES =====")

    # Run the tests
    test_config_loading()
    print("\n" + "-" * 50 + "\n")

    test_send_configured_signal()
    print("\n" + "-" * 50 + "\n")

    test_send_unconfigured_signal()

    logger.info("===== ALL TESTS COMPLETED =====")
