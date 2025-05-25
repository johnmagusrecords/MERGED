import React, { useState } from 'react';
import { Power, Sliders, Lock, Globe, Bell } from 'lucide-react';
import { useTradingBot } from '../hooks/useTradingBot';
import { BotSettings } from '../types/trading';

export default function TradingControls() {
  const { startBot, stopBot, updateStrategy, isRunning } = useTradingBot();
  const [maxPosition, setMaxPosition] = useState('10000');
  const [mode, setMode] = useState<'Safe' | 'Balanced' | 'Aggressive'>('Balanced');
  const [language, setLanguage] = useState<'en' | 'ar'>('en');
  const [settings, setSettings] = useState<BotSettings>({
    mode: 'Balanced',
    language: 'en',
    tradingHours: {
      start: '08:00',
      end: '17:00'
    },
    riskParameters: {
      maxDailyLoss: 1000,
      maxDrawdown: 5,
      maxPositions: 5,
      leverageLimit: 10
    },
    notifications: {
      telegram: true,
      email: true,
      pushNotifications: true
    }
  });

  const handleStrategyUpdate = () => {
    updateStrategy({
      name: `${mode} Strategy`,
      mode,
      maxPositionSize: parseFloat(maxPosition),
      stopLossPercentage: mode === 'Safe' ? 0.02 : mode === 'Balanced' ? 0.05 : 0.1,
      takeProfitLevels: mode === 'Safe' ? [0.05] : mode === 'Balanced' ? [0.05, 0.1] : [0.1, 0.2, 0.3],
      timeframes: ['15m', '1h', '4h'],
      indicators: ['RSI', 'MACD', 'BB', 'ATR']
    });
  };

  return (
    <div className="bg-white rounded-lg shadow p-6" dir={language === 'ar' ? 'rtl' : 'ltr'}>
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-gray-900">Trading Controls</h3>
        <div className="flex space-x-3">
          <Power className={`h-5 w-5 ${isRunning ? 'text-green-500' : 'text-red-500'}`} />
          <Globe className="h-5 w-5 text-gray-500" />
        </div>
      </div>

      <div className="space-y-6">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Trading Mode</label>
            <select
              value={mode}
              onChange={(e) => setMode(e.target.value as 'Safe' | 'Balanced' | 'Aggressive')}
              className="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
            >
              <option value="Safe">Safe</option>
              <option value="Balanced">Balanced</option>
              <option value="Aggressive">Aggressive</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Language</label>
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value as 'en' | 'ar')}
              className="block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
            >
              <option value="en">English</option>
              <option value="ar">العربية</option>
            </select>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">Max Position Size</label>
          <div className="mt-1 relative rounded-md shadow-sm">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <span className="text-gray-500 sm:text-sm">$</span>
            </div>
            <input
              type="text"
              value={maxPosition}
              onChange={(e) => setMaxPosition(e.target.value)}
              className="focus:ring-indigo-500 focus:border-indigo-500 block w-full pl-7 pr-12 sm:text-sm border-gray-300 rounded-md"
              placeholder="0.00"
            />
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Trading Hours (UTC)</label>
            <div className="flex space-x-2">
              <input
                type="time"
                value={settings.tradingHours.start}
                onChange={(e) => setSettings({
                  ...settings,
                  tradingHours: { ...settings.tradingHours, start: e.target.value }
                })}
                className="block w-full pl-3 pr-3 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
              />
              <input
                type="time"
                value={settings.tradingHours.end}
                onChange={(e) => setSettings({
                  ...settings,
                  tradingHours: { ...settings.tradingHours, end: e.target.value }
                })}
                className="block w-full pl-3 pr-3 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Max Daily Loss ($)</label>
            <input
              type="number"
              value={settings.riskParameters.maxDailyLoss}
              onChange={(e) => setSettings({
                ...settings,
                riskParameters: { ...settings.riskParameters, maxDailyLoss: parseInt(e.target.value) }
              })}
              className="block w-full pl-3 pr-3 py-2 text-base border-gray-300 focus:outline-none focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm rounded-md"
            />
          </div>
        </div>

        <div className="flex items-center space-x-4 pt-4">
          <button
            onClick={isRunning ? stopBot : startBot}
            className={`flex-1 inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white ${
              isRunning ? 'bg-red-600 hover:bg-red-700' : 'bg-green-600 hover:bg-green-700'
            } focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500`}
          >
            <Lock className="h-4 w-4 mr-2" />
            {isRunning ? 'Stop Bot' : 'Start Bot'}
          </button>
          <button
            onClick={handleStrategyUpdate}
            className="flex-1 inline-flex items-center justify-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            <Sliders className="h-4 w-4 mr-2" />
            Update Strategy
          </button>
        </div>

        <div className="flex items-center justify-between pt-4 border-t border-gray-200">
          <div className="flex items-center space-x-2">
            <Bell className="h-4 w-4 text-gray-500" />
            <span className="text-sm text-gray-600">Notifications</span>
          </div>
          <div className="flex space-x-4">
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={settings.notifications.telegram}
                onChange={(e) => setSettings({
                  ...settings,
                  notifications: { ...settings.notifications, telegram: e.target.checked }
                })}
                className="form-checkbox h-4 w-4 text-indigo-600"
              />
              <span className="ml-2 text-sm text-gray-600">Telegram</span>
            </label>
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={settings.notifications.email}
                onChange={(e) => setSettings({
                  ...settings,
                  notifications: { ...settings.notifications, email: e.target.checked }
                })}
                className="form-checkbox h-4 w-4 text-indigo-600"
              />
              <span className="ml-2 text-sm text-gray-600">Email</span>
            </label>
          </div>
        </div>
      </div>
    </div>
  );
}