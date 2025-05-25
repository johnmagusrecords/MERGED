import React, { useEffect } from 'react';
import { LineChart, BarChart, Activity, AlertTriangle, TrendingUp, Brain, Settings } from 'lucide-react';
import PositionsTable from './PositionsTable';
import RiskMetrics from './RiskMetrics';
import TradingControls from './TradingControls';
import MarketSentiment from './MarketSentiment';
import VoiceControls from './VoiceControls';
import { useTradingBot } from '../hooks/useTradingBot';

export default function Dashboard() {
  const { startBot, stopBot, positions, riskMetrics, isRunning } = useTradingBot();

  useEffect(() => {
    startBot();
    return () => stopBot();
  }, []);

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8 flex justify-between items-center">
          <div className="flex items-center space-x-3">
            <Activity className="h-8 w-8 text-indigo-600" />
            <h1 className="text-2xl font-bold text-gray-900">MAGUS PRIME X</h1>
          </div>
          <div className="flex items-center space-x-4">
            <div className={`px-3 py-1 rounded-full ${isRunning ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
              {isRunning ? 'Bot Active' : 'Bot Inactive'}
            </div>
            <button className="p-2 rounded-lg hover:bg-gray-100">
              <Settings className="h-5 w-5 text-gray-600" />
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Risk Alert Banner */}
        <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-6">
          <div className="flex items-center">
            <AlertTriangle className="h-5 w-5 text-yellow-400" />
            <p className="ml-3 text-sm text-yellow-700">
              Market volatility is high. Automated risk management is active.
            </p>
          </div>
        </div>

        {/* Grid Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Main Trading View */}
          <div className="lg:col-span-2 space-y-6">
            <div className="bg-white rounded-lg shadow">
              <div className="p-6">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-lg font-semibold text-gray-900">Portfolio Performance</h2>
                  <div className="flex space-x-2">
                    <button className="px-3 py-1 text-sm bg-indigo-50 text-indigo-600 rounded-md">1D</button>
                    <button className="px-3 py-1 text-sm bg-gray-50 text-gray-600 rounded-md">1W</button>
                    <button className="px-3 py-1 text-sm bg-gray-50 text-gray-600 rounded-md">1M</button>
                  </div>
                </div>
                <div className="h-64 bg-gray-50 rounded-lg flex items-center justify-center">
                  <LineChart className="h-8 w-8 text-gray-400" />
                  <span className="ml-2 text-gray-500">Chart Loading...</span>
                </div>
              </div>
            </div>
            <PositionsTable positions={positions} />
          </div>

          {/* Right Sidebar */}
          <div className="space-y-6">
            <RiskMetrics metrics={riskMetrics} />
            <TradingControls />
            <VoiceControls />
            <MarketSentiment />
          </div>
        </div>
      </main>
    </div>
  );
}