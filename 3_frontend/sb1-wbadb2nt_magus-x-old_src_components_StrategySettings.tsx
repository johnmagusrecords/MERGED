import React, { useState } from 'react';
import { Settings, TrendingUp, AlertTriangle, Brain, Target, Shield, Zap } from 'lucide-react';
import { TradingMode } from '../types/trading';

interface StrategySettingsProps {
  onSettingsChange: (settings: any) => void;
  initialSettings?: any;
}

export default function StrategySettings({ onSettingsChange, initialSettings }: StrategySettingsProps) {
  const [settings, setSettings] = useState({
    mode: 'BALANCED' as TradingMode,
    profitTarget: {
      type: 'fixed',
      value: 50,
      currency: 'USD'
    },
    riskLimit: {
      maxDailyLoss: 60,
      maxTotalLoss: 200,
      currency: 'USD'
    },
    capitalPercentage: 2,
    indicators: {
      rsi: true,
      macd: true,
      bollinger: true,
      atr: true,
      vwap: true,
      stochastic: true
    },
    timeframes: {
      '1m': true,
      '5m': true,
      '15m': true,
      '1h': true,
      '4h': true
    },
    recoveryMode: {
      enabled: true,
      maxAttempts: 2,
      sizeMultiplier: 1.5
    },
    newsTrading: {
      enabled: true,
      avoidHighImpact: true,
      tradeLowImpact: false
    },
    marketConditions: {
      tradeSideways: false,
      tradeVolatility: true,
      minVolume: 1000000
    },
    ...initialSettings
  });

  const handleChange = (section: string, field: string, value: any) => {
    const newSettings = {
      ...settings,
      [section]: {
        ...settings[section],
        [field]: value
      }
    };
    setSettings(newSettings);
    onSettingsChange(newSettings);
  };

  const handleModeChange = (mode: TradingMode) => {
    setSettings({ ...settings, mode });
    onSettingsChange({ ...settings, mode });
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6 space-y-8">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <Settings className="h-6 w-6 text-indigo-600" />
          Strategy Settings
        </h2>
      </div>

      {/* Trading Modes */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-900">Trading Mode</h3>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {(['SAFE', 'BALANCED', 'AGGRESSIVE', 'BEAST'] as TradingMode[]).map(mode => (
            <button
              key={mode}
              onClick={() => handleModeChange(mode)}
              className={`p-4 rounded-lg flex flex-col items-center gap-2 transition-all ${
                settings.mode === mode
                  ? 'bg-indigo-100 border-2 border-indigo-500'
                  : 'bg-gray-50 border-2 border-transparent hover:bg-gray-100'
              }`}
            >
              {mode === 'SAFE' && <Shield className="h-6 w-6 text-green-500" />}
              {mode === 'BALANCED' && <TrendingUp className="h-6 w-6 text-blue-500" />}
              {mode === 'AGGRESSIVE' && <Zap className="h-6 w-6 text-orange-500" />}
              {mode === 'BEAST' && <Brain className="h-6 w-6 text-red-500" />}
              <span className="font-medium">{mode}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Profit & Loss Settings */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-900">Profit & Loss Settings</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="space-y-2">
            <label className="block text-sm font-medium text-gray-700">
              Profit Target Type
            </label>
            <select
              value={settings.profitTarget.type}
              onChange={(e) => handleChange('profitTarget', 'type', e.target.value)}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            >
              <option value="fixed">Fixed Amount</option>
              <option value="percentage">Percentage of Capital</option>
            </select>
          </div>
          <div className="space-y-2">
            <label className="block text-sm font-medium text-gray-700">
              Target Value
            </label>
            <input
              type="number"
              value={settings.profitTarget.value}
              onChange={(e) => handleChange('profitTarget', 'value', parseFloat(e.target.value))}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            />
          </div>
          <div className="space-y-2">
            <label className="block text-sm font-medium text-gray-700">
              Max Daily Loss
            </label>
            <input
              type="number"
              value={settings.riskLimit.maxDailyLoss}
              onChange={(e) => handleChange('riskLimit', 'maxDailyLoss', parseFloat(e.target.value))}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            />
          </div>
          <div className="space-y-2">
            <label className="block text-sm font-medium text-gray-700">
              Max Total Loss
            </label>
            <input
              type="number"
              value={settings.riskLimit.maxTotalLoss}
              onChange={(e) => handleChange('riskLimit', 'maxTotalLoss', parseFloat(e.target.value))}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            />
          </div>
        </div>
      </div>

      {/* Technical Indicators */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-900">Technical Indicators</h3>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          {Object.entries(settings.indicators).map(([indicator, enabled]) => (
            <label key={indicator} className="flex items-center space-x-3">
              <input
                type="checkbox"
                checked={enabled as boolean}
                onChange={(e) => handleChange('indicators', indicator, e.target.checked)}
                className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
              />
              <span className="text-sm font-medium text-gray-700 uppercase">{indicator}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Timeframes */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-900">Timeframes</h3>
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          {Object.entries(settings.timeframes).map(([timeframe, enabled]) => (
            <label key={timeframe} className="flex items-center space-x-3">
              <input
                type="checkbox"
                checked={enabled as boolean}
                onChange={(e) => handleChange('timeframes', timeframe, e.target.checked)}
                className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
              />
              <span className="text-sm font-medium text-gray-700">{timeframe}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Recovery Mode */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-900">Recovery Mode</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <label className="flex items-center space-x-3">
            <input
              type="checkbox"
              checked={settings.recoveryMode.enabled}
              onChange={(e) => handleChange('recoveryMode', 'enabled', e.target.checked)}
              className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
            />
            <span className="text-sm font-medium text-gray-700">Enable Recovery Mode</span>
          </label>
          <div className="space-y-2">
            <label className="block text-sm font-medium text-gray-700">
              Max Recovery Attempts
            </label>
            <input
              type="number"
              value={settings.recoveryMode.maxAttempts}
              onChange={(e) => handleChange('recoveryMode', 'maxAttempts', parseInt(e.target.value))}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            />
          </div>
          <div className="space-y-2">
            <label className="block text-sm font-medium text-gray-700">
              Size Multiplier
            </label>
            <input
              type="number"
              step="0.1"
              value={settings.recoveryMode.sizeMultiplier}
              onChange={(e) => handleChange('recoveryMode', 'sizeMultiplier', parseFloat(e.target.value))}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            />
          </div>
        </div>
      </div>

      {/* News Trading */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-900">News Trading</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <label className="flex items-center space-x-3">
            <input
              type="checkbox"
              checked={settings.newsTrading.enabled}
              onChange={(e) => handleChange('newsTrading', 'enabled', e.target.checked)}
              className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
            />
            <span className="text-sm font-medium text-gray-700">Enable News Trading</span>
          </label>
          <label className="flex items-center space-x-3">
            <input
              type="checkbox"
              checked={settings.newsTrading.avoidHighImpact}
              onChange={(e) => handleChange('newsTrading', 'avoidHighImpact', e.target.checked)}
              className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
            />
            <span className="text-sm font-medium text-gray-700">Avoid High Impact News</span>
          </label>
          <label className="flex items-center space-x-3">
            <input
              type="checkbox"
              checked={settings.newsTrading.tradeLowImpact}
              onChange={(e) => handleChange('newsTrading', 'tradeLowImpact', e.target.checked)}
              className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
            />
            <span className="text-sm font-medium text-gray-700">Trade Low Impact News</span>
          </label>
        </div>
      </div>

      {/* Market Conditions */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-gray-900">Market Conditions</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <label className="flex items-center space-x-3">
            <input
              type="checkbox"
              checked={settings.marketConditions.tradeSideways}
              onChange={(e) => handleChange('marketConditions', 'tradeSideways', e.target.checked)}
              className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
            />
            <span className="text-sm font-medium text-gray-700">Trade Sideways Markets</span>
          </label>
          <label className="flex items-center space-x-3">
            <input
              type="checkbox"
              checked={settings.marketConditions.tradeVolatility}
              onChange={(e) => handleChange('marketConditions', 'tradeVolatility', e.target.checked)}
              className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
            />
            <span className="text-sm font-medium text-gray-700">Trade High Volatility</span>
          </label>
          <div className="space-y-2">
            <label className="block text-sm font-medium text-gray-700">
              Minimum Volume (USD)
            </label>
            <input
              type="number"
              value={settings.marketConditions.minVolume}
              onChange={(e) => handleChange('marketConditions', 'minVolume', parseInt(e.target.value))}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
            />
          </div>
        </div>
      </div>

      {/* Save Button */}
      <div className="pt-5">
        <div className="flex justify-end">
          <button
            type="button"
            onClick={() => onSettingsChange(settings)}
            className="ml-3 inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            Save Settings
          </button>
        </div>
      </div>
    </div>
  );
}