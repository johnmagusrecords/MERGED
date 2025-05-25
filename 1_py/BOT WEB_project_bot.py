"""
Main AI Trading Bot Logic with Telegram Integration
"""
from typing import Dict, List, Optional
import logging
from datetime import datetime
import asyncio
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from strategies.strategy1 import Strategy1
from strategies.strategy2 import Strategy2
from risk_management.risk_assessment import RiskAssessment
from risk_management.position_sizing import PositionSizing
from config import Config
from signal_processor import SignalProcessor

class TradingBot:
    def __init__(self, config: Config):
        self.config = config
        self.logger = self._setup_logger()
        self.risk_manager = RiskAssessment(config)
        self.position_sizer = PositionSizing(config)
        self.signal_processor = SignalProcessor(config)
        self.telegram_bot = None
        self.strategies = {
            'strategy1': Strategy1(config),
            'strategy2': Strategy2(config)
        }
        
    def _setup_logger(self) -> logging.Logger:
        logger = logging.getLogger('TradingBot')
        logger.setLevel(logging.INFO if not self.config.DEBUG else logging.DEBUG)
        
        if self.config.LOG_TO_FILE:
            fh = logging.FileHandler(self.config.LOG_FILE)
            fh.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
            logger.addHandler(fh)
            
        return logger
    
    async def setup_telegram(self):
        """Initialize Telegram bot and handlers"""
        self.telegram_bot = Application.builder().token(self.config.TELEGRAM_TOKEN).build()
        
        # Command handlers
        self.telegram_bot.add_handler(CommandHandler("start", self._handle_start))
        self.telegram_bot.add_handler(CommandHandler("status", self._handle_status))
        
        # Message handler for trading signals
        self.telegram_bot.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            self._handle_signal
        ))
        
        # Error handler
        self.telegram_bot.add_error_handler(self._handle_error)
        
    async def _handle_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_message = (
            "🤖 Welcome to MAGUS PRIME X Trading Bot!\n\n"
            "I'll help you receive and process trading signals.\n"
            "Use /status to check the bot's current status."
        )
        await update.message.reply_text(welcome_message)
        
    async def _handle_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        status = self.get_bot_status()
        await update.message.reply_text(status)
        
    async def _handle_signal(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Process incoming trading signals"""
        try:
            signal = self.signal_processor.parse_message(update.message.text)
            if signal:
                # Process the signal
                await self._process_trading_signal(signal)
                # Notify success
                response = self._format_signal_response(signal)
                await update.message.reply_text(response, parse_mode='HTML')
        except Exception as e:
            self.logger.error(f"Error processing signal: {e}")
            await update.message.reply_text("Error processing signal. Please try again.")
            
    async def _handle_error(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors in Telegram bot"""
        self.logger.error(f"Telegram error: {context.error}")
        
    async def start(self):
        """Start the trading bot and Telegram listener"""
        self.logger.info("Starting trading bot...")
        try:
            # Start Telegram bot
            await self.setup_telegram()
            asyncio.create_task(self.telegram_bot.run_polling())
            
            # Start trading loop
            while True:
                await self._trading_loop()
        except Exception as e:
            self.logger.error(f"Error in main loop: {e}")
            raise
            
    async def _trading_loop(self):
        """Main trading loop"""
        try:
            if self.config.STRATEGY_MODE == "Balanced":
                await self._run_balanced_strategy()
            elif self.config.STRATEGY_MODE == "Aggressive":
                await self._run_aggressive_strategy()
            elif self.config.STRATEGY_MODE == "Safe":
                await self._run_safe_strategy()
                
            await asyncio.sleep(int(self.config.TRADE_INTERVAL))
        except Exception as e:
            self.logger.error(f"Error in trading loop: {e}")
            
    async def _process_trading_signal(self, signal: Dict):
        """Process a trading signal and execute if conditions are met"""
        try:
            # Validate signal
            if not self.signal_processor.validate_signal(signal):
                return
                
            # Check risk parameters
            risk_assessment = self.risk_manager.assess_trade_risk(signal)
            if not risk_assessment['approved']:
                self.logger.warning(f"Signal rejected: {risk_assessment['reason']}")
                return
                
            # Calculate position size
            position_size = self.position_sizer.calculate_position_size(
                capital=self.get_available_capital(),
                risk_per_trade=float(self.config.RISK_PERCENT),
                stop_loss=signal['stop_loss']
            )
            
            # Execute trade if automated trading is enabled
            if self.config.CAPITAL_API_ENV == 'live':
                await self._execute_trade(signal, position_size)
                
        except Exception as e:
            self.logger.error(f"Error processing trading signal: {e}")
            
    def _format_signal_response(self, signal: Dict) -> str:
        """Format signal response for Telegram"""
        return f"""
<b>🎯 New Trading Signal</b>

Symbol: {signal['symbol']}
Type: {signal['type']}
Entry: {signal['entry']}
Stop Loss: {signal['stop_loss']}
Take Profit 1: {signal['tp1']}
Take Profit 2: {signal['tp2']}
Take Profit 3: {signal['tp3']}

⚠️ Risk Management:
Max Position Size: ${self.config.MAX_POSITIONS}
Recommended Leverage: {signal.get('leverage', '1:1')}
"""
        
    def get_bot_status(self) -> str:
        """Get current bot status"""
        return f"""
🤖 MAGUS PRIME X Status

Mode: {self.config.STRATEGY_MODE}
API Environment: {self.config.CAPITAL_API_ENV}
Active Positions: {len(self.get_active_positions())}
Daily P&L: ${self.get_daily_pnl()}
Risk Level: {self.risk_manager.get_current_risk_level()}
"""
        
    def get_active_positions(self) -> List[Dict]:
        """Get list of active trading positions"""
        # Implementation for getting active positions
        return []
        
    def get_daily_pnl(self) -> float:
        """Get daily profit/loss"""
        # Implementation for calculating daily P&L
        return 0.0
        
    def get_available_capital(self) -> float:
        """Get available trading capital"""
        # Implementation for getting available capital
        return 10000.0  # Default value