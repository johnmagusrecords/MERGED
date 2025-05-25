import os
import json
import time
import logging
import threading
import datetime
import requests

# Configure logging first
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Try to import optional dependencies
try:
    from dotenv import load_dotenv
    # Load environment variables from .env file
    load_dotenv()
    logger.info("Environment variables loaded from .env file")
except ImportError:
    # dotenv module not installed
    print("Warning: python-dotenv package not installed. Using system environment variables only.")
    print("To install required dependencies, run: install_dependencies.bat")
    
    # Define a dummy load_dotenv function to prevent errors
    def load_dotenv():
        """Dummy function when dotenv is not available"""
        return None

from templates import (
    generate_signal_message, 
    generate_recap_message, 
    get_pre_signal_message, 
    get_recovery_message
)
from gpt_commentary import get_gpt_commentary

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_GROUP_ID")
GROUP_ID = os.getenv("TELEGRAM_GROUP_ID") or os.getenv("TELEGRAM_GROUP_ID")
CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")

MAGUS_ASSISTANT_ENABLED = os.getenv("MAGUS_ASSISTANT_ENABLED", "false").lower() == "true"

# Try to import optional dependencies
try:
    from market_status_checker import check_market_status, get_available_assets
    MARKET_STATUS_AVAILABLE = True
except ImportError:
    MARKET_STATUS_AVAILABLE = False
    logger.warning("Market status checker not available")

try:
    from news_monitor import get_market_sentiment
    NEWS_MONITOR_AVAILABLE = True
except ImportError:
    NEWS_MONITOR_AVAILABLE = False
    logger.warning("News monitor not available")

try:
    from openai_assistant import get_trade_commentary
    ASSISTANT_AVAILABLE = True
    logger.info("MAGUS PRIMEX ASSISTANT integration available for signals")
except ImportError:
    ASSISTANT_AVAILABLE = False
    logger.warning("MAGUS PRIMEX ASSISTANT integration not available")

class EnhancedSignalSender:
    """
    Enhanced signal sender with pre-signals, recaps, and recovery signals
    Implements the complete signal flow and integrates with market status checking
    """
    
    def __init__(self):
        # Initialize from environment variables
        self.telegram_token = BOT_TOKEN
        self.telegram_chat_id = CHAT_ID
        self.telegram_group_id = GROUP_ID
        self.telegram_channel_id = CHANNEL_ID
        
        # Feature flags
        self.pre_signals_enabled = True
        self.recovery_mode_enabled = True
        self.market_awareness_enabled = MARKET_STATUS_AVAILABLE
        self.commentary_enabled = True
        self.magus_assistant_enabled = MAGUS_ASSISTANT_ENABLED
        
        # Track active signals for recaps
        self.active_signals = {}
        self.signal_history = []
        
        # Start the recap monitoring thread
        self.stop_event = threading.Event()
        self.recap_thread = threading.Thread(target=self.monitor_signals, daemon=True)
        self.recap_thread.start()
        logger.info("Signal monitoring thread started")

    def send_telegram_message(self, text, parse_mode="Markdown"):
        """Send a message to Telegram targets (chat, group, and channel)"""
        results = {}
        
        # Try to send to all configured targets
        targets = []
        if self.telegram_chat_id:
            targets.append(("personal", self.telegram_chat_id))
        if self.telegram_group_id:
            targets.append(("group", self.telegram_group_id))
        if self.telegram_channel_id:
            targets.append(("channel", self.telegram_channel_id))
            
        if not targets:
            logger.error("No Telegram targets configured")
            return {"error": "No targets configured"}
            
        for target_name, target_id in targets:
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            payload = {
                "chat_id": target_id,
                "text": text,
                "parse_mode": parse_mode
            }
            try:
                response = requests.post(url, json=payload, timeout=10)
                
                if response.status_code == 200:
                    result = response.json()
                    message_id = result.get("result", {}).get("message_id")
                    logger.info(f"Message sent to {target_name} successfully (ID: {message_id})")
                    results[target_name] = {"success": True, "message_id": message_id}
                else:
                    logger.error(f"Failed to send message to {target_name}: {response.status_code} - {response.text}")
                    results[target_name] = {"error": f"Status code: {response.status_code}", "details": response.text}
            except Exception as e:
                logger.error(f"Error sending message to {target_name}: {e}")
                results[target_name] = {"error": str(e)}
        
        # Return success if any target was successful
        for result in results.values():
            if result.get("success"):
                return {"success": True, "results": results}
                
        return {"error": "Failed to send message to any target", "details": results}
    
    def send_pre_signal_alert(self, pair, direction=None, strategy=None, timeframe=None):
        """Send a pre-signal alert before the main signal"""
        if not self.pre_signals_enabled:
            logger.info("Pre-signals are disabled, skipping")
            return {"success": False, "reason": "Pre-signals disabled"}
        
        # Check if market is open for this pair
        if self.market_awareness_enabled and not check_market_status(pair):
            logger.warning(f"Market for {pair} is closed, skipping pre-signal")
            return {"success": False, "reason": "Market closed"}
        
        # Use simple format if strategy not provided
        if not strategy:
            alert_text = f"🚨 *Incoming Signal Alert*\nPreparing high-accuracy trade setup for *{pair}*..."
            return self.send_telegram_message(alert_text)
        else:
            # Generate structured pre-signal message
            message = get_pre_signal_message(pair, direction, strategy, timeframe or "30m")
            return self.send_telegram_message(message, parse_mode="HTML")
    
    def send_signal(self, pair, direction, entry, stop_loss, take_profits, 
                   asset_type=None, strategy=None, timeframe=None, hold_time=None, 
                   commentary=None, generate_pre_signal=True):
        """
        Send a complete trading signal with advanced features
        
        Args:
            pair: Trading pair/symbol
            direction: BUY or SELL
            entry: Entry price
            stop_loss: Stop loss price
            take_profits: List of take profit prices [tp1, tp2, tp3]
            asset_type: Asset type (Crypto, Forex, etc.)
            strategy: Signal type/strategy
            timeframe: Chart timeframe
            hold_time: Expected hold time
            commentary: Custom commentary text (optional)
            generate_pre_signal: Whether to send a pre-signal first
            
        Returns:
            dict: Response data with signal details
        """
        try:
            # Normalize and validate inputs
            pair = pair.upper()
            direction = direction.upper()
            
            # Extract take profit values
            tp1 = take_profits[0] if take_profits and len(take_profits) > 0 else None
            tp2 = take_profits[1] if take_profits and len(take_profits) > 1 else None
            tp3 = take_profits[2] if take_profits and len(take_profits) > 2 else None
                
            # Check if market is open
            if self.market_awareness_enabled and not check_market_status(pair):
                logger.warning(f"Market for {pair} is closed, skipping signal")
                return {"error": "Market closed"}
                
            # Optionally send pre-signal
            if generate_pre_signal and self.pre_signals_enabled:
                pre_result = self.send_pre_signal_alert(pair, direction, strategy, timeframe)
                logger.info(f"Pre-signal sent for {pair}: {pre_result}")
                
                # Small delay between pre-signal and main signal
                time.sleep(5)
                
            # Generate technical commentary
            if self.commentary_enabled and not commentary:
                # First try to use the AI assistant if available
                if ASSISTANT_AVAILABLE and self.magus_assistant_enabled:
                    try:
                        # Format targets for the assistant
                        targets = [t for t in [tp1, tp2, tp3] if t is not None]
                        
                        ai_commentary = get_trade_commentary(
                            symbol=pair, 
                            direction=direction,
                            entry=entry,
                            stop_loss=stop_loss,
                            targets=targets,
                            strategy=strategy or "Technical"
                        )
                        
                        if ai_commentary:
                            commentary = ai_commentary
                    except Exception as e:
                        logger.error(f"Error using AI assistant for commentary: {e}")
                
                # Fall back to GPT commentary if AI assistant failed or unavailable
                if not commentary:
                    try:
                        commentary = get_gpt_commentary(pair, direction, strategy or "Technical")
                    except Exception as e:
                        logger.error(f"Error getting GPT commentary: {e}")
                        commentary = f"Analyzing {direction} setup based on {strategy} strategy."
            
            # Generate the signal message
            msg = generate_signal_message(
                pair=pair,
                direction=direction,
                entry=entry,
                stop_loss=stop_loss,
                take_profits=take_profits,
                asset_type=asset_type or "Unknown",
                strategy=strategy or "Technical",
                timeframe=timeframe or "30m",
                hold_time=hold_time or "Medium-term",
                commentary=commentary
            )
            
            # Send to Telegram
            result = self.send_telegram_message(msg)
            
            if result.get("success"):
                # Store the signal for later recap
                signal_id = str(int(time.time()))
                signal_data = {
                    "id": signal_id,
                    "pair": pair,
                    "direction": direction,
                    "entry": entry,
                    "stop_loss": stop_loss,
                    "tp1": tp1,
                    "tp2": tp2,
                    "tp3": tp3,
                    "timeframe": timeframe,
                    "strategy": strategy,
                    "asset_type": asset_type,
                    "timestamp": datetime.datetime.now().isoformat(),
                    "status": "active",
                    "message_id": result.get("message_id")
                }
                
                self.active_signals[signal_id] = signal_data
                
                # Return success with the signal data
                return {
                    "success": True,
                    "signal_id": signal_id,
                    "message_id": result.get("message_id"),
                    "signal_data": signal_data
                }
            else:
                return {"error": "Failed to send signal message", "details": result}
                
        except Exception as e:
            logger.error(f"Error sending signal: {e}")
            return {"error": str(e)}
    
    def send_recap(self, pair, result, exit_price, notes=None, signal_id=None):
        """
        Send a recap message for a completed signal
        
        Args:
            pair: Trading pair/symbol
            result: Trade result ("WIN", "LOSS", "BREAK EVEN")
            exit_price: Exit price
            notes: Additional notes (optional)
            signal_id: ID of the signal to recap (optional)
            
        Returns:
            dict: Response from Telegram
        """
        try:
            # If signal_id is provided, get the signal data
            signal = None
            if signal_id and signal_id in self.active_signals:
                signal = self.active_signals[signal_id]
                pair = signal["pair"]
            else:
                # Look for active signal with matching pair
                for s_id, s_data in self.active_signals.items():
                    if s_data["pair"] == pair:
                        signal = s_data
                        signal_id = s_id
                        break
            
            # Determine hit targets based on exit price
            hit_tp1 = False
            hit_tp2 = False
            hit_tp3 = False
            hit_sl = False
            
            # If we found a matching signal, determine what targets were hit
            if signal:
                direction = signal["direction"]
                exit_price = float(exit_price) if isinstance(exit_price, str) else exit_price
                
                if direction == "BUY":
                    hit_sl = exit_price <= float(signal["stop_loss"])
                    
                    if "tp1" in signal and signal["tp1"]:
                        hit_tp1 = exit_price >= float(signal["tp1"])
                    if "tp2" in signal and signal["tp2"]:
                        hit_tp2 = exit_price >= float(signal["tp2"])
                    if "tp3" in signal and signal["tp3"]:
                        hit_tp3 = exit_price >= float(signal["tp3"])
                else:  # SELL
                    hit_sl = exit_price >= float(signal["stop_loss"])
                    
                    if "tp1" in signal and signal["tp1"]:
                        hit_tp1 = exit_price <= float(signal["tp1"])
                    if "tp2" in signal and signal["tp2"]:
                        hit_tp2 = exit_price <= float(signal["tp2"])
                    if "tp3" in signal and signal["tp3"]:
                        hit_tp3 = exit_price <= float(signal["tp3"])
            
            # Generate the recap message
            if signal:
                # Use the more detailed format
                recap_msg = generate_recap_message(
                    pair, 
                    result, 
                    exit_price, 
                    notes,
                    entry=signal.get("entry"),
                    targets_hit={
                        "tp1": hit_tp1,
                        "tp2": hit_tp2,
                        "tp3": hit_tp3,
                        "sl": hit_sl
                    }
                )
            else:
                # Use the simple format
                recap_msg = generate_recap_message(pair, result, exit_price, notes)
            
            # Send to Telegram
            result = self.send_telegram_message(recap_msg)
            
            # Update signal records if we found a matching signal
            if signal and signal_id:
                # Update signal status
                signal["status"] = "closed"
                signal["recap"] = {
                    "hit_tp1": hit_tp1,
                    "hit_tp2": hit_tp2,
                    "hit_tp3": hit_tp3,
                    "hit_sl": hit_sl,
                    "exit_price": exit_price,
                    "result": result,
                    "notes": notes,
                    "timestamp": datetime.datetime.now().isoformat()
                }
                
                # Move to history
                self.signal_history.append(signal)
                
                # Remove from active signals
                del self.active_signals[signal_id]
                
                # Send recovery signal if SL was hit and recovery mode is enabled
                if hit_sl and self.recovery_mode_enabled:
                    self.send_recovery_signal(signal)
            
            return result
                
        except Exception as e:
            logger.error(f"Error sending recap: {e}")
            return {"error": str(e)}
    
    def send_recovery_signal(self, original_signal):
        """
        Send a recovery signal after a stop loss is hit
        
        Args:
            original_signal: Original signal data that hit stop loss
            
        Returns:
            dict: Response from signal sender
        """
        try:
            if not self.recovery_mode_enabled:
                logger.info("Recovery mode is disabled, skipping recovery signal")
                return {"success": False, "reason": "Recovery mode disabled"}
                
            # Get signal parameters
            pair = original_signal["pair"]
            direction = original_signal["direction"]
            original_entry = float(original_signal["entry"])
            original_sl = float(original_signal["stop_loss"])
            timeframe = original_signal.get("timeframe", "30m")
            
            # Determine new entry, stop loss, and take profit levels
            # For a recovery signal, we often reverse the direction
            new_direction = "BUY" if direction == "SELL" else "SELL"
            
            # Calculate new levels based on the original signal
            # For simplicity, using the original SL as new entry
            new_entry = original_sl
            
            # New SL is a percentage beyond the entry in the new direction
            sl_distance = abs(original_entry - original_sl)
            new_sl = new_entry - sl_distance if new_direction == "BUY" else new_entry + sl_distance
            
            # TP is 1.5x, 2x, and 3x the distance in the favorable direction
            new_tp1 = new_entry + (sl_distance * 1.5) if new_direction == "BUY" else new_entry - (sl_distance * 1.5)
            new_tp2 = new_entry + (sl_distance * 2.0) if new_direction == "BUY" else new_entry - (sl_distance * 2.0)
            new_tp3 = new_entry + (sl_distance * 3.0) if new_direction == "BUY" else new_entry - (sl_distance * 3.0)
            
            # Create recovery type (original strategy + Recovery)
            recovery_strategy = f"{original_signal.get('strategy', 'Technical')} Recovery"
            
            # Generate and send the recovery message using the same function
            return self.send_signal(
                pair=pair,
                direction=new_direction,
                entry=new_entry,
                stop_loss=new_sl,
                take_profits=[new_tp1, new_tp2, new_tp3],
                asset_type=original_signal.get("asset_type"),
                strategy=recovery_strategy,
                timeframe=timeframe,
                hold_time="Short-term",
                commentary=f"Recovery signal after previous {direction} hit stop loss at {original_sl}. Looking for reversal movement.",
                generate_pre_signal=False
            )
                
        except Exception as e:
            logger.error(f"Error sending recovery signal: {e}")
            return {"error": str(e)}
    
    def monitor_signals(self):
        """Background thread that monitors active signals"""
        while not self.stop_event.is_set():
            try:
                # Sleep for a while to avoid excessive checking
                time.sleep(120)  # Check every 2 minutes
                
                # Skip if no active signals
                if not self.active_signals:
                    continue
                    
                # Check each active signal
                for signal_id, signal in list(self.active_signals.items()):
                    # Skip signals that have been active for more than 7 days
                    timestamp = datetime.datetime.fromisoformat(signal["timestamp"])
                    if (datetime.datetime.now() - timestamp).days > 7:
                        logger.info(f"Signal {signal_id} for {signal['pair']} expired (>7 days)")
                        
                        # Close with unknown result
                        self.send_recap(
                            signal["pair"], 
                            "EXPIRED", 
                            signal["entry"],  # Use entry as exit since we don't know actual exit
                            "Signal expired after 7 days",
                            signal_id
                        )
                        continue
                    
                # In a real implementation, this is where you'd check if price has hit targets
                # For now, this is just a placeholder
                    
            except Exception as e:
                logger.error(f"Error in signal monitoring: {e}")
    
    def stop(self):
        """Stop the signal monitoring thread"""
        self.stop_event.set()
        self.recap_thread.join(timeout=1.0)
        logger.info("Signal monitoring thread stopped")
    
    def get_active_signals(self):
        """Get a list of current active signals"""
        return list(self.active_signals.values())
    
    def get_signal_history(self):
        """Get the signal history"""
        return self.signal_history
    
    def save_signal_history(self, filename="signal_history.json"):
        """
        Save the signal history to a JSON file
        
        Args:
            filename: Name of the file to save to
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(os.path.abspath(filename)), exist_ok=True)
            
            # Convert signal history to serializable format
            serializable_history = []
            for signal in self.signal_history:
                signal_copy = signal.copy()
                # Filter out any datetime objects or non-serializable values
                for key, value in list(signal_copy.items()):
                    if isinstance(value, (datetime.datetime, datetime.date)):
                        signal_copy[key] = value.isoformat()
                serializable_history.append(signal_copy)
            
            # Save to file
            with open(filename, 'w') as f:
                json.dump(serializable_history, f, indent=2)
                
            logger.info(f"Signal history saved to {os.path.abspath(filename)}")
            return True
        except Exception as e:
            logger.error(f"Error saving signal history: {e}")
            return False
    
    def load_signal_history(self, filename="signal_history.json"):
        """
        Load signal history from a JSON file
        
        Args:
            filename: Name of the file to load from
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Check if file exists
            if not os.path.exists(filename):
                logger.warning(f"Signal history file not found: {filename}")
                return False
                
            # Load from file
            with open(filename, 'r') as f:
                loaded_history = json.load(f)
                
            # Process loaded history
            self.signal_history = loaded_history
            logger.info(f"Signal history loaded from {os.path.abspath(filename)}")
            return True
        except Exception as e:
            logger.error(f"Error loading signal history: {e}")
            return False

# Create a global instance
signal_dispatcher = EnhancedSignalSender()

# Backwards compatibility functions
def send_telegram_message(text, parse_mode="Markdown"):
    """Legacy function for direct Telegram message sending"""
    return signal_dispatcher.send_telegram_message(text, parse_mode=parse_mode)

def send_pre_signal_alert(pair):
    """Legacy function for pre-signal alerts"""
    return signal_dispatcher.send_pre_signal_alert(pair)

def send_signal(pair, direction, entry, stop_loss, take_profits, asset_type=None, strategy=None, timeframe=None, hold_time=None, commentary=None):
    """
    Global function to send a trading signal (legacy format)
    """
    return signal_dispatcher.send_signal(
        pair, direction, entry, stop_loss, take_profits,
        asset_type, strategy, timeframe, hold_time, commentary
    )

def send_recap(pair, result, exit_price, notes=None):
    """
    Global function to send a signal recap (legacy format)
    """
    return signal_dispatcher.send_recap(pair, result, exit_price, notes)

# Modify the implementation of send_signal_to_telegram to avoid circular imports
def format_and_send_signal(signal_data, tag=""):
    """Send a formatted signal to Telegram (compatibility function)"""
    try:
        # Format signal data into a message
        message = f"{tag} SIGNAL\n\n"
        message += f"Pair: {signal_data.get('pair')}\n"
        message += f"Direction: {signal_data.get('direction')}\n"
        message += f"Entry: {signal_data.get('entry')}\n"
        message += f"SL: {signal_data.get('stop_loss')}\n"

        # Add TPs
        take_profits = signal_data.get("take_profits", [])
        if take_profits and len(take_profits) > 0:
            message += f"TP1: {take_profits[0]}\n"
        if take_profits and len(take_profits) > 1:
            message += f"TP2: {take_profits[1]}\n"
        if take_profits and len(take_profits) > 2:
            message += f"TP3: {take_profits[2]}\n"

        message += f"\nStrategy: {signal_data.get('strategy', 'Recovery')}"

        if signal_data.get("commentary"):
            message += f"\n\n{signal_data.get('commentary')}"

        # Use the local instance directly instead of importing
        return signal_dispatcher.send_telegram_message(message, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Error sending signal to Telegram: {e}")
        return None

def send_signal_to_telegram(chat_id, message):
    """
    Send a signal message to Telegram
    
    Args:
        chat_id (str): The Telegram chat ID to send the message to
        message (str): The message to send
    
    Returns:
        bool: True if the message was sent successfully, False otherwise
    """
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": 'HTML'
        }
        response = requests.post(url, json=payload, timeout=10)
        
        if response.status_code == 200:
            logging.info(f"Signal sent to Telegram: {message[:50]}...")
            return True
        else:
            logging.error(f"Failed to send signal to Telegram. Status code: {response.status_code}")
            return False
    except Exception as e:
        logging.error(f"Failed to send signal to Telegram: {e}")
        return False

def start_signal_monitor():
    """
    Legacy function to start the signal monitor (no-op as it's started automatically)
    """
    logger.info("Signal monitoring thread already started")
    return True

# Demonstration code when run directly
if __name__ == "__main__":
    print("Enhanced Signal Sender Test")
    print("-" * 60)
    
    # Test sending a signal
    print("\nSending test signal for BTCUSD...")
    result = send_signal(
        pair="BTCUSD",
        direction="BUY",
        entry=72000,
        stop_loss=71000,
        take_profits=[73000, 74000, 75000],
        timeframe="4h",
        strategy="Breakout"
    )
    
    if result.get("success"):
        print(f"✅ Signal sent successfully! ID: {result['signal_id']}")
        
        # Store the signal ID for recap test
        signal_id = result["signal_id"]
        
        # Wait a bit before sending recap
        print("\nWaiting 5 seconds before sending recap...")
        time.sleep(5)
        
        # Test sending a recap
        print("\nSending test recap (TP1 hit)...")
        recap_result = send_recap(
            pair="BTCUSD",
            result="WIN",
            exit_price=73000,
            notes="Target 1 reached"
        )
        
        if isinstance(recap_result, dict) and recap_result.get("success"):
            print("✅ Recap sent successfully!")
        else:
            print(f"❌ Failed to send recap: {recap_result}")
    else:
        print(f"❌ Failed to send signal: {result}")
    
    print("\nEnhanced Signal Sender is running in the background.")
    print("Press Ctrl+C to stop...")
    
    try:
        # Keep the main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping signal dispatcher...")
        signal_dispatcher.stop()
        print("Done!")