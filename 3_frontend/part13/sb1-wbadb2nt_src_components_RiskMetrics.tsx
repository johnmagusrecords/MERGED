import React from 'react';
import { Shield, TrendingDown, AlertCircle } from 'lucide-react';
import { RiskMetrics as RiskMetricsType } from '../types/trading';

const mockMetrics: RiskMetricsType = {
  var: 2500,
  cvar: 3200,
  drawdown: 1.2,
  maxDrawdown: 5.8
};

export default function RiskMetrics() {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Risk Metrics</h3>
        <Shield className="h-5 w-5 text-indigo-600" />
      </div>
      <div className="space-y-4">
        <div className="flex justify-between items-center">
          <div className="flex items-center">
            <AlertCircle className="h-4 w-4 text-gray-400 mr-2" />
            <span className="text-sm text-gray-600">Value at Risk (VaR)</span>
          </div>
          <span className="text-sm font-medium text-gray-900">${mockMetrics.var.toLocaleString()}</span>
        </div>
        <div className="flex justify-between items-center">
          <div className="flex items-center">
            <AlertCircle className="h-4 w-4 text-gray-400 mr-2" />
            <span className="text-sm text-gray-600">Conditional VaR</span>
          </div>
          <span className="text-sm font-medium text-gray-900">${mockMetrics.cvar.toLocaleString()}</span>
        </div>
        <div className="flex justify-between items-center">
          <div className="flex items-center">
            <TrendingDown className="h-4 w-4 text-gray-400 mr-2" />
            <span className="text-sm text-gray-600">Current Drawdown</span>
          </div>
          <span className="text-sm font-medium text-gray-900">{mockMetrics.drawdown}%</span>
        </div>
        <div className="flex justify-between items-center">
          <div className="flex items-center">
            <TrendingDown className="h-4 w-4 text-gray-400 mr-2" />
            <span className="text-sm text-gray-600">Max Drawdown</span>
          </div>
          <span className="text-sm font-medium text-gray-900">{mockMetrics.maxDrawdown}%</span>
        </div>
      </div>
    </div>
  );
}