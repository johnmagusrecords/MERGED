import React, { useEffect, useState } from 'react';
import { LineChart, Activity, AlertTriangle, TrendingUp, Brain, Settings } from 'lucide-react';
import PositionsTable from './PositionsTable';
import RiskMetrics from './RiskMetrics';
import TradingControls from './TradingControls';
import MarketSentiment from './MarketSentiment';
import VoiceControls from './VoiceControls';
import ProjectTracker from './ProjectTracker';
import { useTradingBot } from '../hooks/useTradingBot';

export default function Dashboard() {
  const { startBot, stopBot, positions, riskMetrics, isRunning } = useTradingBot();
  const [showSettings, setShowSettings] = useState(false);

  useEffect(() => {
    startBot();
    return () => stopBot();
  }, []);

  return (
    <div className="space-y-6">
      {/* Status Banner */}
      <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4">
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

          <div className="bg-white rounded-lg shadow overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-200">
              <h3 className="text-lg font-semibold text-gray-900">Active Positions</h3>
            </div>
            <PositionsTable positions={positions} />
          </div>

          <ProjectTracker />
        </div>

        {/* Right Sidebar */}
        <div className="space-y-6">
          <RiskMetrics metrics={riskMetrics} />
          <TradingControls />
          <VoiceControls />
          <MarketSentiment />
        </div>
      </div>
    </div>
  );
}