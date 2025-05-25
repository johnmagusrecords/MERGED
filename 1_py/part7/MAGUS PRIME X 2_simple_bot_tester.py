import logging
import random
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("bot_tester.log"), logging.StreamHandler()],
)

# Simulation settings
INITIAL_BALANCE = 10000.0
SIMULATION_DAYS = 30
SYMBOLS = [
    "EURUSD",
    "GBPUSD",
    "USDJPY",
    "AUDUSD",
    "BTCUSD",
    "ETHUSD",
    "US30",
    "US500",
    "GOLD",
]


# Strategy parameters
class Strategy:
    def __init__(
        self,
        name,
        risk_percent,
        tp_move_percent,
        breakeven_trigger,
        trade_interval,
        atr_multiplier_tp=2.5,
        atr_multiplier_sl=1.5,
    ):
        self.name = name
        self.risk_percent = risk_percent
        self.tp_move_percent = tp_move_percent
        self.breakeven_trigger = breakeven_trigger
        self.trade_interval = trade_interval
        self.atr_multiplier_tp = atr_multiplier_tp
        self.atr_multiplier_sl = atr_multiplier_sl

    def __str__(self):
        return (
            f"Strategy: {self.name}, Risk: {self.risk_percent}%, "
            f"TP Move: {self.tp_move_percent*100}%, BE Trigger: {self.breakeven_trigger*100}%"
        )


# Define strategies
STRATEGIES = {
    "Safe": Strategy("Safe", 1, 0.003, 0.005, 600),
    "Balanced": Strategy("Balanced", 2, 0.005, 0.010, 300),
    "Aggressive": Strategy("Aggressive", 3, 0.010, 0.015, 120),
}


class TradingBot:
    def __init__(self):
        self.active_trades = {}
        self.closed_trades = []
        self.balance = INITIAL_BALANCE
        self.equity = INITIAL_BALANCE
        self.market_data = {}
        self.trade_count = 0
        self.win_count = 0
        self.loss_count = 0
        self.current_strategy = STRATEGIES["Balanced"]

        logging.info("Bot initialized with balance: $%.2f", self.balance)
        logging.info(str(self.current_strategy))

    def set_strategy(self, strategy_name):
        """Change the bot's strategy"""
        if strategy_name in STRATEGIES:
            self.current_strategy = STRATEGIES[strategy_name]
            logging.info("Strategy changed to: %s", strategy_name)
            logging.info(str(self.current_strategy))
            return True
        else:
            logging.error("Unknown strategy: %s", strategy_name)
            return False

    def generate_market_data(self, symbol, days=30, interval=15):
        """Generate simulated market data for a symbol"""
        # Base prices for different symbols
        base_prices = {
            "EURUSD": 1.1850,
            "GBPUSD": 1.3650,
            "USDJPY": 110.50,
            "AUDUSD": 0.7450,
            "BTCUSD": 55000,
            "ETHUSD": 3500,
            "US30": 35000,
            "US500": 4500,
            "GOLD": 1850,
        }

        base_price = base_prices.get(symbol, 100)
        volatility = base_price * 0.002  # 0.2% volatility

        # Generate time series
        end_time = datetime.now()
        start_time = end_time - timedelta(days=days)
        date_range = pd.date_range(
            start=start_time, end=end_time, freq=f"{interval}min"
        )

        # Generate prices
        prices = []
        current_price = base_price

        for _ in range(len(date_range)):
            # Random walk with drift
            price_change = np.random.normal(0, volatility)
            current_price += price_change

            # Generate OHLC data
            high_low_range = abs(price_change) * 1.5
            open_price = current_price - (price_change / 2)
            close_price = current_price
            high_price = max(open_price, close_price) + (high_low_range / 2)
            low_price = min(open_price, close_price) - (high_low_range / 2)
            volume = random.randint(1000, 10000)

            prices.append(
                {
                    "open": open_price,
                    "high": high_price,
                    "low": low_price,
                    "close": close_price,
                    "volume": volume,
                }
            )

        # Create DataFrame
        df = pd.DataFrame(prices, index=date_range)
        return df

    def calculate_indicators(self, data):
        """Calculate technical indicators for market data"""
        df = data.copy()

        # Calculate EMA 200
        df["ema200"] = df["close"].ewm(span=200, adjust=False).mean()

        # Calculate RSI
        delta = df["close"].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()
        rs = avg_gain / avg_loss
        df["rsi"] = 100 - (100 / (1 + rs))

        # Calculate MACD
        df["ema12"] = df["close"].ewm(span=12, adjust=False).mean()
        df["ema26"] = df["close"].ewm(span=26, adjust=False).mean()
        df["macd"] = df["ema12"] - df["ema26"]
        df["signal"] = df["macd"].ewm(span=9, adjust=False).mean()
        df["macd_hist"] = df["macd"] - df["signal"]

        # Calculate ATR
        high_low = df["high"] - df["low"]
        high_close = abs(df["high"] - df["close"].shift())
        low_close = abs(df["low"] - df["close"].shift())
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        df["atr"] = true_range.rolling(14).mean()

        return df

    def analyze_market(self, symbol):
        """Analyze market data and generate trading signals"""
        if symbol not in self.market_data:
            self.market_data[symbol] = self.calculate_indicators(
                self.generate_market_data(symbol)
            )

        df = self.market_data[symbol].copy()
        current = df.iloc[-1]

        # Basic analysis
        price = current["close"]
        ema200 = current["ema200"]
        rsi = current["rsi"]
        macd = current["macd"]
        macd_signal = current["signal"]
        atr = current["atr"]

        # Determine signal
        signal = "NEUTRAL"
        signal_strength = 0

        # Trend direction
        trend = "UP" if price > ema200 else "DOWN"

        # RSI conditions
        if rsi > 70:
            signal_strength -= 1
            rsi_condition = "OVERBOUGHT"
        elif rsi < 30:
            signal_strength += 1
            rsi_condition = "OVERSOLD"
        else:
            rsi_condition = "NEUTRAL"

        # MACD conditions
        if macd > macd_signal and macd > 0:
            signal_strength += 1
            macd_condition = "BULLISH"
        elif macd < macd_signal and macd < 0:
            signal_strength -= 1
            macd_condition = "BEARISH"
        else:
            macd_condition = "NEUTRAL"

        # Final signal based on overall conditions
        if signal_strength > 0:
            signal = "BUY"
        elif signal_strength < 0:
            signal = "SELL"

        # Random factor to make it more realistic
        if random.random() < 0.2:  # 20% chance to flip the signal
            signal = (
                "BUY" if signal == "SELL" else "SELL" if signal == "BUY" else "NEUTRAL"
            )

        return {
            "symbol": symbol,
            "price": price,
            "ema200": ema200,
            "rsi": rsi,
            "rsi_condition": rsi_condition,
            "macd": macd,
            "macd_condition": macd_condition,
            "atr": atr,
            "trend": trend,
            "signal": signal,
            "timestamp": df.index[-1],
        }

    def calculate_position_size(self, symbol, risk_percent):
        """Calculate position size based on account balance and risk percentage"""
        analysis = self.analyze_market(symbol)
        analysis["price"]
        atr = analysis["atr"]

        # Risk amount in dollars
        risk_amount = self.balance * (risk_percent / 100)

        # Stop loss distance (using ATR)
        sl_distance = atr * self.current_strategy.atr_multiplier_sl

        # Calculate position size
        position_size = risk_amount / sl_distance

        # Round to 2 decimal places
        position_size = round(position_size, 2)

        return max(0.01, position_size)  # Minimum position size of 0.01

    def calculate_stop_loss(self, price, direction, atr):
        """Calculate stop loss level based on direction and ATR"""
        multiplier = self.current_strategy.atr_multiplier_sl
        if direction == "BUY":
            return price - (atr * multiplier)
        else:
            return price + (atr * multiplier)

    def calculate_take_profit(self, price, direction, atr):
        """Calculate take profit level based on direction and ATR"""
        multiplier = self.current_strategy.atr_multiplier_tp
        if direction == "BUY":
            return price + (atr * multiplier)
        else:
            return price - (atr * multiplier)

    def execute_trade(self, symbol, direction):
        """Execute a simulated trade"""
        self.trade_count += 1
        deal_id = f"TRADE-{self.trade_count}"

        # Get market data and calculate levels
        analysis = self.analyze_market(symbol)
        price = analysis["price"]
        atr = analysis["atr"]

        # Calculate position size, stop loss, and take profit
        position_size = self.calculate_position_size(
            symbol, self.current_strategy.risk_percent
        )
        stop_loss = self.calculate_stop_loss(price, direction, atr)
        take_profit = self.calculate_take_profit(price, direction, atr)

        # Create trade record
        trade = {
            "id": deal_id,
            "symbol": symbol,
            "direction": direction,
            "open_price": price,
            "current_price": price,
            "stop_loss": stop_loss,
            "take_profit": take_profit,
            "position_size": position_size,
            "open_time": datetime.now(),
            "status": "OPEN",
            "pnl": 0,
        }

        # Add to active trades
        self.active_trades[deal_id] = trade

        logging.info("Trade executed: %s %s at %.5f", direction, symbol, price)
        logging.info(
            "Position Size: %.2f, SL: %.5f, TP: %.5f",
            position_size,
            stop_loss,
            take_profit,
        )

        return deal_id

    def update_trades(self):
        """Update all active trades - check for SL/TP hits and update prices"""
        for deal_id, trade in list(self.active_trades.items()):
            symbol = trade["symbol"]
            direction = trade["direction"]

            # Get current price
            analysis = self.analyze_market(symbol)
            current_price = analysis["price"]

            # Update current price
            trade["current_price"] = current_price

            # Calculate P/L
            if direction == "BUY":
                pnl = (current_price - trade["open_price"]) * trade["position_size"]
                pnl_percent = (
                    (current_price - trade["open_price"]) / trade["open_price"] * 100
                )
            else:  # SELL
                pnl = (trade["open_price"] - current_price) * trade["position_size"]
                pnl_percent = (
                    (trade["open_price"] - current_price) / trade["open_price"] * 100
                )

            trade["pnl"] = pnl
            trade["pnl_percent"] = pnl_percent

            # Breakeven logic
            if pnl_percent >= self.current_strategy.breakeven_trigger * 100:
                if direction == "BUY" and trade["stop_loss"] < trade["open_price"]:
                    trade["stop_loss"] = trade["open_price"]
                    logging.info("Moving SL to breakeven: %s %s", symbol, deal_id)
                elif direction == "SELL" and trade["stop_loss"] > trade["open_price"]:
                    trade["stop_loss"] = trade["open_price"]
                    logging.info("Moving SL to breakeven: %s %s", symbol, deal_id)

            # Take profit trailing logic
            if pnl_percent >= self.current_strategy.tp_move_percent * 100:
                tp_movement = current_price * self.current_strategy.tp_move_percent
                if direction == "BUY":
                    new_tp = trade["take_profit"] + tp_movement
                    if new_tp > trade["take_profit"]:
                        trade["take_profit"] = new_tp
                        logging.info(
                            "Trailing TP up: %s %s to %.5f", symbol, deal_id, new_tp
                        )
                else:  # SELL
                    new_tp = trade["take_profit"] - tp_movement
                    if new_tp < trade["take_profit"]:
                        trade["take_profit"] = new_tp
                        logging.info(
                            "Trailing TP down: %s %s to %.5f", symbol, deal_id, new_tp
                        )

            # Check for SL/TP hit
            if direction == "BUY":
                if current_price <= trade["stop_loss"]:
                    self.close_trade(deal_id, "Stop Loss")
                elif current_price >= trade["take_profit"]:
                    self.close_trade(deal_id, "Take Profit")
            else:  # SELL
                if current_price >= trade["stop_loss"]:
                    self.close_trade(deal_id, "Stop Loss")
                elif current_price <= trade["take_profit"]:
                    self.close_trade(deal_id, "Take Profit")

        # Update equity
        self.update_equity()

    def close_trade(self, deal_id, reason="Manual"):
        """Close a trade and record the result"""
        if deal_id not in self.active_trades:
            logging.warning("Trade %s not found", deal_id)
            return False

        trade = self.active_trades[deal_id]
        symbol = trade["symbol"]
        direction = trade["direction"]
        open_price = trade["open_price"]

        # Determine closing price
        if reason == "Stop Loss":
            close_price = trade["stop_loss"]
        elif reason == "Take Profit":
            close_price = trade["take_profit"]
        else:
            close_price = trade["current_price"]

        # Calculate P/L
        if direction == "BUY":
            pnl = (close_price - open_price) * trade["position_size"]
        else:  # SELL
            pnl = (open_price - close_price) * trade["position_size"]

        # Update trade record
        trade["close_price"] = close_price
        trade["close_time"] = datetime.now()
        trade["pnl"] = pnl
        trade["status"] = "CLOSED"
        trade["close_reason"] = reason

        # Update balance
        self.balance += pnl

        # Update win/loss counts
        if pnl > 0:
            self.win_count += 1
        else:
            self.loss_count += 1

        # Add to closed trades and remove from active
        self.closed_trades.append(trade)
        del self.active_trades[deal_id]

        logging.info("Trade closed: %s %s, Reason: %s", direction, symbol, reason)
        logging.info(
            "Entry: %.5f, Exit: %.5f, P/L: $%.2f", open_price, close_price, pnl
        )

        return True

    def update_equity(self):
        """Update equity based on balance and open trade P/Ls"""
        unrealized_pnl = sum(trade["pnl"] for trade in self.active_trades.values())
        self.equity = self.balance + unrealized_pnl

    def run_simulation(self, days=1):
        """Run a trading simulation for a specified number of days"""
        logging.info("Starting simulation for %d days", days)
        logging.info("Initial balance: $%.2f", self.balance)

        # Configure time steps
        start_time = datetime.now()
        end_time = start_time + timedelta(days=days)
        current_time = start_time

        # Track last trade time
        last_trade_time = start_time - timedelta(
            minutes=self.current_strategy.trade_interval
        )

        # Main simulation loop
        while current_time < end_time:
            # Advance time by 15 minutes
            current_time += timedelta(minutes=15)

            # Update all active trades
            self.update_trades()

            # Check if it's time for a new trade
            time_since_last_trade = (
                current_time - last_trade_time
            ).total_seconds() / 60
            if time_since_last_trade >= self.current_strategy.trade_interval:
                # Choose a random symbol
                symbol = random.choice(SYMBOLS)

                # Analyze market
                analysis = self.analyze_market(symbol)
                signal = analysis["signal"]

                # Execute trade if clear signal
                if (
                    signal in ["BUY", "SELL"] and len(self.active_trades) < 5
                ):  # Limit to 5 active trades
                    self.execute_trade(symbol, signal)
                    last_trade_time = current_time

            # Print summary every 4 hours of simulation time
            if current_time.hour % 4 == 0 and current_time.minute == 0:
                self.print_summary()

        # Final summary
        logging.info("Simulation completed")
        self.print_summary()

    def print_summary(self):
        """Print trading summary"""
        logging.info("--- Trading Summary ---")
        logging.info("Balance: $%.2f", self.balance)
        logging.info("Equity: $%.2f", self.equity)
        logging.info("Active Trades: %d", len(self.active_trades))
        logging.info("Closed Trades: %d", len(self.closed_trades))
        logging.info(
            "Win/Loss: %d/%d (%.1f%%)",
            self.win_count,
            self.loss_count,
            (self.win_count / max(1, self.win_count + self.loss_count)) * 100,
        )

        # Print active trades
        if self.active_trades:
            logging.info("Active Trades:")
            for _deal_id, trade in self.active_trades.items():
                logging.info(
                    "  %s %s: Entry: %.5f, Current: %.5f, P/L: $%.2f",
                    trade["direction"],
                    trade["symbol"],
                    trade["open_price"],
                    trade["current_price"],
                    trade["pnl"],
                )

        # Calculate average profit and loss
        if self.closed_trades:
            profits = [t["pnl"] for t in self.closed_trades if t["pnl"] > 0]
            losses = [t["pnl"] for t in self.closed_trades if t["pnl"] <= 0]

            avg_profit = sum(profits) / max(1, len(profits))
            avg_loss = sum(losses) / max(1, len(losses))

            logging.info("Average Profit: $%.2f", avg_profit)
            logging.info("Average Loss: $%.2f", avg_loss)
            logging.info(
                "Profit Factor: %.2f",
                abs(avg_profit / avg_loss) if avg_loss != 0 else 0,
            )


# Interactive console for testing
def interactive_console():
    print("\n=== MAGUS PRIME X Bot Tester ===")
    print("Type 'help' for a list of commands")

    bot = TradingBot()

    while True:
        try:
            command = input("\nCommand> ").strip().lower()

            if command == "help":
                print("\nAvailable commands:")
                print("  simulate <days> - Run a simulation for specified days")
                print("  strategy <safe|balanced|aggressive> - Change strategy")
                print("  analyze <symbol> - Analyze a symbol")
                print("  trade <symbol> <buy|sell> - Execute a test trade")
                print("  close <trade_id> - Close a specific trade")
                print("  closeall - Close all trades")
                print("  status - Show current status")
                print("  summary - Print summary")
                print("  exit - Exit the program")

            elif command.startswith("simulate "):
                try:
                    days = float(command.split()[1])
                    bot.run_simulation(days)
                except (IndexError, ValueError):
                    print("Usage: simulate <days>")

            elif command.startswith("strategy "):
                try:
                    strategy_name = command.split()[1].capitalize()
                    if bot.set_strategy(strategy_name):
                        print(f"Strategy changed to {strategy_name}")
                    else:
                        print(f"Unknown strategy: {strategy_name}")
                except IndexError:
                    print("Usage: strategy <safe|balanced|aggressive>")

            elif command.startswith("analyze "):
                try:
                    symbol = command.split()[1].upper()
                    analysis = bot.analyze_market(symbol)
                    print(f"\nAnalysis for {symbol}:")
                    print(f"Price: {analysis['price']:.5f}")
                    print(f"EMA200: {analysis['ema200']:.5f}")
                    print(f"RSI: {analysis['rsi']:.2f} ({analysis['rsi_condition']})")
                    print(
                        f"MACD: {analysis['macd']:.5f} ({analysis['macd_condition']})"
                    )
                    print(f"ATR: {analysis['atr']:.5f}")
                    print(f"Trend: {analysis['trend']}")
                    print(f"Signal: {analysis['signal']}")
                except IndexError:
                    print("Usage: analyze <symbol>")

            elif command.startswith("trade "):
                parts = command.split()
                if len(parts) != 3:
                    print("Usage: trade <symbol> <buy|sell>")
                else:
                    symbol = parts[1].upper()
                    direction = parts[2].upper()
                    if direction not in ["BUY", "SELL"]:
                        print("Direction must be BUY or SELL")
                    else:
                        deal_id = bot.execute_trade(symbol, direction)
                        print(f"Trade executed with ID: {deal_id}")

            elif command.startswith("close "):
                try:
                    deal_id = command.split()[1]
                    if bot.close_trade(deal_id, "Manual"):
                        print(f"Trade {deal_id} closed")
                    else:
                        print(f"Trade {deal_id} not found")
                except IndexError:
                    print("Usage: close <trade_id>")

            elif command == "closeall":
                for deal_id in list(bot.active_trades.keys()):
                    bot.close_trade(deal_id, "Manual")
                print("All trades closed")

            elif command == "status":
                print(f"\nStrategy: {bot.current_strategy.name}")
                print(f"Balance: ${bot.balance:.2f}")
                print(f"Equity: ${bot.equity:.2f}")
                print(f"Active Trades: {len(bot.active_trades)}")
                if bot.active_trades:
                    print("\nActive Trades:")
                    for deal_id, trade in bot.active_trades.items():
                        print(
                            f" "
  {deal_id}: {trade['direction']} {trade + "['symbol']} @ {trade['open_price']:.5f}"
                        )
                        print(
                            f"    Current: {trade['current_price']:.5f}, P/L: ${trade['pnl']:.2f}"
                        )
                        print(
                            f"    SL: {trade['stop_loss']:.5f}, TP: {trade['take_profit']:.5f}"
                        )

            elif command == "summary":
                bot.print_summary()

            elif command == "exit":
                print("Exiting Bot Tester")
                break

            else:
                print("Unknown command. Type 'help' for available commands.")

        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {str(e)}")


if __name__ == "__main__":
    interactive_console()
