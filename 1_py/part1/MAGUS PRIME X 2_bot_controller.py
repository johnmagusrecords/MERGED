import logging
import os
import sys
import threading
import time

# Import the TradingBot class from bot.py
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from bot_dev_backup import (
    BREAKEVEN_TRIGGER,
    RISK_PERCENT,
    STRATEGY_MODE,
    TP_MOVE_PERCENT,
    TradingBot,
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("bot_controller.log"), logging.StreamHandler()],
)


class BotController:
    def __init__(self):
        self.bot = None
        self.monitor_thread = None
        self.is_running = False
        self.strategy_mode = STRATEGY_MODE
        self.risk_percent = RISK_PERCENT
        self.tp_move_percent = TP_MOVE_PERCENT
        self.breakeven_trigger = BREAKEVEN_TRIGGER

        logging.info("Bot Controller initialized")

    def start_bot(self):
        """Start the trading bot"""
        try:
            logging.info("Starting bot with strategy: " + self.strategy_mode)
            self.bot = TradingBot()

            # Check if we can connect to Capital.com
            cst, security = self.bot.authenticate()
            if not cst or not security:
                logging.error("Failed to authenticate with Capital.com")
                return False

            logging.info("Successfully authenticated with Capital.com")

            # Start bot monitoring thread
            self.is_running = True
            self.monitor_thread = threading.Thread(target=self.monitor_bot)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()

            # Test the market data
            self.test_market_data()

            return True
        except Exception as e:
            logging.error(f"Error starting bot: {str(e)}")
            return False

    def stop_bot(self):
        """Stop the trading bot"""
        try:
            logging.info("Stopping bot")
            self.is_running = False
            if self.bot:
                # Close all trades if any
                for symbol in list(self.bot.active_trades.keys()):
                    logging.info(f"Closing trade for {symbol}")
                    self.bot.close_trade(symbol, "Bot Stopped")

            logging.info("Bot stopped successfully")
            return True
        except Exception as e:
            logging.error(f"Error stopping bot: {str(e)}")
            return False

    def monitor_bot(self):
        """Monitor bot activities in a separate thread"""
        logging.info("Bot monitoring started")
        while self.is_running:
            try:
                if self.bot:
                    # Get account info
                    account_info = self.bot.get_account_info()
                    if account_info:
                        logging.info(f"Account Balance: ${account_info['balance']:.2f}")

                    # Check active trades
                    active_trades = self.bot.active_trades
                    if active_trades:
                        logging.info(f"Active Trades: {len(active_trades)}")
                        for symbol, trade in active_trades.items():
                            logging.info(
                                f" "
  {symbol}: {trade['direction']} Entry:  + "{trade['entry_price']:.5f} SL: {trade['s + "top_loss']:.5f} TP: {trade['take_profit' + "]:.5f}"
                            )

                    # Update active trades
                    self.bot.update_active_trades()

            except Exception as e:
                logging.error(f"Error in bot monitoring: {str(e)}")

            time.sleep(5)  # Check every 5 seconds

        logging.info("Bot monitoring stopped")

    def change_strategy(self, strategy_mode):
        """Change the strategy mode"""
        try:
            if strategy_mode not in ["Safe", "Balanced", "Aggressive"]:
                logging.error(f"Invalid strategy mode: {strategy_mode}")
                return False

            logging.info(
                f"Changing strategy from {self.strategy_mode} to {strategy_mode}"
            )
            self.strategy_mode = strategy_mode

            # Update strategy parameters
            if strategy_mode == "Safe":
                self.risk_percent = 1
                self.tp_move_percent = 0.3 / 100
                self.breakeven_trigger = 0.5 / 100
            elif strategy_mode == "Aggressive":
                self.risk_percent = 3
                self.tp_move_percent = 1 / 100
                self.breakeven_trigger = 1.5 / 100
            else:  # Balanced
                self.risk_percent = 2
                self.tp_move_percent = 0.5 / 100
                self.breakeven_trigger = 1 / 100

            # Update global variables (these are used by the bot)
            global RISK_PERCENT, TP_MOVE_PERCENT, BREAKEVEN_TRIGGER
            RISK_PERCENT = self.risk_percent
            TP_MOVE_PERCENT = self.tp_move_percent
            BREAKEVEN_TRIGGER = self.breakeven_trigger

            logging.info(
                f" "
Strategy updated: Risk={
                                                self.risk_percen + "t}%,
                                                TP Move={self.tp_move_percent*100}% + ",
                                                BE Trigger={self.breakeven_trigger*100 + "}%"            )
            return True
        except Exception as e:
            logging.error(f"Error changing strategy: {str(e)}")
            return False

    def test_market_data(self):
        """Test market data retrieval and analysis"""
        try:
            test_symbols = ["EURUSD", "BTCUSD", "GOLD", "US30"]
            logging.info("Testing market data for symbols: " + ", ".join(test_symbols))

            for symbol in test_symbols:
                logging.info(f"Analyzing {symbol}...")

                # Get market data
                market_data = self.bot.get_market_data(symbol)
                if market_data is not None:
                    logging.info(f"  {symbol} data retrieved successfully")

                    # Analyze market
                    analysis = self.bot.analyze_market(symbol)
                    if analysis:
                        logging.info(f"  {symbol} Analysis: {analysis['signal']}")
                        logging.info(f"  Current Price: {analysis['price']:.5f}")
                        logging.info(
                            f" "
  Indicators: EMA200={
                                                          analysis[
                                                                   'ema200'] + ":.5f},
                                                          RSI={analysis['rsi']:.2f}"                        )
                else:
                    logging.warning(f"  Failed to get market data for {symbol}")
        except Exception as e:
            logging.error(f"Error testing market data: {str(e)}")

    def execute_test_trade(self, symbol, direction):
        """Execute a test trade"""
        try:
            if not self.bot:
                logging.error("Bot not started")
                return False

            logging.info(f"Executing test trade: {direction} {symbol}")

            # Calculate ATR for stop loss and take profit
            atr = self.bot.calculate_atr(symbol)
            if atr is None:
                logging.error(f"Could not calculate ATR for {symbol}")
                return False

            # Get current price
            price_data = self.bot.get_market_data(symbol)
            if not price_data:
                logging.error(f"Could not get price data for {symbol}")
                return False

            current_price = price_data["close"].iloc[-1]

            # Calculate stop loss and take profit
            if direction == "BUY":
                stop_loss = current_price - (atr * 1.5)
                take_profit = current_price + (atr * 2.5)
            else:
                stop_loss = current_price + (atr * 1.5)
                take_profit = current_price - (atr * 2.5)

            # Execute the trade
            result = self.bot.execute_trade(symbol, direction, take_profit, stop_loss)

            if result:
                logging.info("Trade executed successfully")
                logging.info(f"  Symbol: {symbol}")
                logging.info(f"  Direction: {direction}")
                logging.info(f"  Entry: {current_price:.5f}")
                logging.info(f"  Stop Loss: {stop_loss:.5f}")
                logging.info(f"  Take Profit: {take_profit:.5f}")
                return True
            else:
                logging.error("Failed to execute trade")
                return False
        except Exception as e:
            logging.error(f"Error executing test trade: {str(e)}")
            return False

    def interactive_console(self):
        """Start an interactive console for bot control"""
        print("\n=== MAGUS PRIME X Bot Controller ===")
        print("Type 'help' for a list of commands")

        while True:
            try:
                command = input("\nCommand> ").strip().lower()

                if command == "help":
                    print("\nAvailable commands:")
                    print("  start - Start the trading bot")
                    print("  stop - Stop the trading bot")
                    print("  status - Show bot status")
                    print("  safe - Switch to Safe strategy")
                    print("  balanced - Switch to Balanced strategy")
                    print("  aggressive - Switch to Aggressive strategy")
                    print("  trade <symbol> <buy/sell> - Execute a test trade")
                    print("  markets - Test market data retrieval")
                    print("  exit - Exit the controller")

                elif command == "start":
                    if self.start_bot():
                        print("Bot started successfully")
                    else:
                        print("Failed to start bot")

                elif command == "stop":
                    if self.stop_bot():
                        print("Bot stopped successfully")
                    else:
                        print("Failed to stop bot")

                elif command == "status":
                    if not self.bot:
                        print("Bot not started")
                    else:
                        print(f"Bot is running: {self.is_running}")
                        print(f"Strategy: {self.strategy_mode}")
                        print(f"Risk: {self.risk_percent}%")
                        print(f"TP Move: {self.tp_move_percent*100}%")
                        print(f"BE Trigger: {self.breakeven_trigger*100}%")
                        print(f"Active Trades: {len(self.bot.active_trades)}")

                elif command == "safe":
                    if self.change_strategy("Safe"):
                        print("Changed to Safe strategy")
                    else:
                        print("Failed to change strategy")

                elif command == "balanced":
                    if self.change_strategy("Balanced"):
                        print("Changed to Balanced strategy")
                    else:
                        print("Failed to change strategy")

                elif command == "aggressive":
                    if self.change_strategy("Aggressive"):
                        print("Changed to Aggressive strategy")
                    else:
                        print("Failed to change strategy")

                elif command.startswith("trade "):
                    parts = command.split()
                    if len(parts) != 3:
                        print("Usage: trade <symbol> <buy/sell>")
                    else:
                        symbol = parts[1].upper()
                        direction = parts[2].upper()
                        if direction not in ["BUY", "SELL"]:
                            print("Direction must be BUY or SELL")
                        else:
                            if self.execute_test_trade(symbol, direction):
                                print(f"{direction} trade executed for {symbol}")
                            else:
                                print("Failed to execute trade")

                elif command == "markets":
                    if not self.bot:
                        print("Bot not started")
                    else:
                        print("Testing market data retrieval...")
                        self.test_market_data()

                elif command == "exit":
                    if self.is_running:
                        self.stop_bot()
                    print("Exiting Bot Controller")
                    break

                else:
                    print("Unknown command. Type 'help' for available commands.")

            except KeyboardInterrupt:
                print("\nExiting...")
                if self.is_running:
                    self.stop_bot()
                break
            except Exception as e:
                print(f"Error: {str(e)}")


if __name__ == "__main__":
    controller = BotController()
    controller.interactive_console()
