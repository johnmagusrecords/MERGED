import React from 'react';
import Dashboard from './components/Dashboard';
import { useEffect } from 'react';
import { botService } from './services/BotService';
import { BotSettings, TradingStrategy } from './types/trading';

function App() {
  useEffect(() => {
    // Initialize bot with environment variables
    const strategy: TradingStrategy = {
      name: import.meta.env.VITE_APP_NAME || 'MAGUS PRIME X',
      mode: (import.meta.env.VITE_STRATEGY_MODE as 'Safe' | 'Balanced' | 'Aggressive') || 'Balanced',
      maxPositionSize: Number(import.meta.env.VITE_MAX_POSITIONS) || 10000,
      stopLossPercentage: Number(import.meta.env.VITE_RISK_PERCENT) / 100 || 0.02,
      takeProfitLevels: [0.05, 0.1, 0.15],
      timeframes: (import.meta.env.VITE_SCALPING_TIMEFRAMES ? 
        JSON.parse(import.meta.env.VITE_SCALPING_TIMEFRAMES) : 
        ['1m', '5m', '15m', '1h', '4h', '1d']),
      indicators: ['RSI', 'MACD', 'MA'],
      symbols: (import.meta.env.VITE_SYMBOLS ? 
        JSON.parse(import.meta.env.VITE_SYMBOLS) : 
        ['BTC/USD', 'ETH/USD']) // Default symbols if none provided
    };

    const settings: BotSettings = {
      mode: (import.meta.env.VITE_STRATEGY_MODE as 'Safe' | 'Balanced' | 'Aggressive') || 'Balanced',
      language: 'en',
      tradingHours: {
        start: '00:00',
        end: '23:59'
      },
      riskParameters: {
        maxDailyLoss: Number(import.meta.env.VITE_DAILY_LOSS_LIMIT) || 1000,
        maxDrawdown: 5,
        maxPositions: Number(import.meta.env.VITE_MAX_POSITIONS) || 5,
        leverageLimit: 10
      },
      notifications: {
        telegram: true,
        email: true,
        pushNotifications: true
      }
    };

    botService.initializeBot(strategy, settings);
  }, []);

  return (
    <div className="min-h-screen bg-gray-50">
      <Dashboard />
    </div>
  );
}

export default App;