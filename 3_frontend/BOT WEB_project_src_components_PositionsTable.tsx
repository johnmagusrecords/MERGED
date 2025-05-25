import React from 'react';
import { TradePosition } from '../types/trading';

const mockPositions: TradePosition[] = [
  {
    symbol: 'BTC/USD',
    entryPrice: 45000,
    currentPrice: 46500,
    quantity: 0.5,
    pnl: 750,
    pnlPercentage: 3.33
  },
  {
    symbol: 'ETH/USD',
    entryPrice: 3000,
    currentPrice: 2950,
    quantity: 2,
    pnl: -100,
    pnlPercentage: -1.67
  }
];

export default function PositionsTable() {
  return (
    <div className="px-6 pb-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Active Positions</h3>
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead>
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Symbol</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Entry Price</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Current Price</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Quantity</th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">P&L</th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {mockPositions.map((position) => (
              <tr key={position.symbol}>
                <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{position.symbol}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${position.entryPrice.toLocaleString()}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">${position.currentPrice.toLocaleString()}</td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{position.quantity}</td>
                <td className={`px-6 py-4 whitespace-nowrap text-sm ${position.pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  ${position.pnl.toLocaleString()} ({position.pnlPercentage}%)
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}