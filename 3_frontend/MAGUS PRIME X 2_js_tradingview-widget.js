/**
 * TradingView Chart Widget Integration
 * Creates and manages a TradingView Advanced Chart widget
 */

let tradingViewWidget = null;

/**
 * Initialize the TradingView widget in the specified container
 * @param {string} containerId - ID of the container element
 * @param {string} symbol - Trading symbol to display (e.g., 'BTCUSD')
 * @param {string} interval - Chart interval (e.g., '15m', '1h', '1d')
 */
function initTradingViewWidget(
  containerId,
  symbol = "BTCUSD",
  interval = "15m",
) {
  // Convert interval to TradingView format
  const tvInterval = convertIntervalToTradingView(interval);

  const container = document.getElementById(containerId);
  if (!container) {
    console.error(`Container element with ID '${containerId}' not found`);
    return;
  }

  // Clear the container
  container.innerHTML = "";

  // Create the TradingView widget
  tradingViewWidget = new TradingView.widget({
    container_id: containerId,
    symbol: symbol,
    interval: tvInterval,
    timezone: "exchange",
    theme: "dark",
    style: "1",
    locale: "en",
    toolbar_bg: "#1b1e29",
    enable_publishing: false,
    allow_symbol_change: true,
    save_image: true,
    studies: ["RSI@tv-basicstudies", "MACD@tv-basicstudies"],
    show_popup_button: true,
    popup_width: "1000",
    popup_height: "650",
    withdateranges: true,
    hide_side_toolbar: false,
    details: true,
    hotlist: true,
    calendar: true,
    studies_overrides: {
      "volume.volume.color.0": "rgba(255, 59, 48, 0.5)",
      "volume.volume.color.1": "rgba(0, 200, 83, 0.5)",
      "RSI.plot.color": "#b46aff",
      "MACD.fast line.color": "#ff3b30",
      "MACD.slow line.color": "#1e90ff",
      "MACD.histogram.color": "#00c853",
    },
    overrides: {
      "mainSeriesProperties.candleStyle.upColor": "#00c853",
      "mainSeriesProperties.candleStyle.downColor": "#ff3b30",
      "mainSeriesProperties.candleStyle.borderUpColor": "#00c853",
      "mainSeriesProperties.candleStyle.borderDownColor": "#ff3b30",
      "mainSeriesProperties.candleStyle.wickUpColor": "#00c853",
      "mainSeriesProperties.candleStyle.wickDownColor": "#ff3b30",
      "paneProperties.background": "#1b1e29",
      "paneProperties.vertGridProperties.color": "#2c3040",
      "paneProperties.horzGridProperties.color": "#2c3040",
      "scalesProperties.textColor": "#8a8d93",
    },
  });

  // Make the widget accessible globally
  window.tradingViewWidget = {
    widget: tradingViewWidget,

    // Method to change the interval
    setInterval: function (interval) {
      const tvInterval = convertIntervalToTradingView(interval);
      tradingViewWidget.chart().setResolution(tvInterval);
    },

    // Method to change the symbol
    setSymbol: function (symbol) {
      tradingViewWidget.chart().setSymbol(symbol);
    },

    // Method to add a study
    addStudy: function (study) {
      tradingViewWidget.chart().createStudy(study);
    },

    // Method to add shapes/drawings
    addShape: function (params) {
      tradingViewWidget.chart().createShape(params);
    },
  };

  return tradingViewWidget;
}

/**
 * Convert our app's interval format to TradingView format
 * @param {string} interval - App interval (e.g., '15m', '1h', '1d')
 * @returns {string} - TradingView interval
 */
function convertIntervalToTradingView(interval) {
  // Map our interval format to TradingView format
  const intervalMap = {
    "1m": "1",
    "5m": "5",
    "15m": "15",
    "30m": "30",
    "1h": "60",
    "2h": "120",
    "4h": "240",
    "1d": "D",
    "1w": "W",
  };

  return intervalMap[interval] || "15"; // Default to 15m if not found
}

// Expose initialization function globally
window.initTradingViewWidget = initTradingViewWidget;

// Load TradingView library dynamically
function loadTradingViewLibrary() {
  return new Promise((resolve, reject) => {
    // Check if the library is already loaded
    if (window.TradingView) {
      resolve();
      return;
    }

    const script = document.createElement("script");
    script.type = "text/javascript";
    script.src = "https://s3.tradingview.com/tv.js";
    script.async = true;

    script.onload = () => resolve();
    script.onerror = (error) =>
      reject(new Error(`Failed to load TradingView library: ${error}`));

    document.head.appendChild(script);
  });
}

// Load the TradingView library when the page loads
document.addEventListener("DOMContentLoaded", () => {
  loadTradingViewLibrary()
    .then(() => {
      console.log("TradingView library loaded successfully");
    })
    .catch((error) => {
      console.error("Error loading TradingView library:", error);
    });
});
