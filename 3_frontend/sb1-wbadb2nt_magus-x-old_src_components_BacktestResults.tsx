import React from 'react';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

interface BacktestResultsProps {
  metrics: {
    totalTrades: number;
    winRate: number;
    profitFactor: number;
    sharpeRatio: number;
    maxDrawdown: number;
    averageWin: number;
    averageLoss: number;
    largestWin: number;
    largestLoss: number;
    averageHoldingTime: number;
  };
  equity: number[];
  drawdown: number[];
}

export default function BacktestResults({
  metrics,
  equity,
  drawdown
}: BacktestResultsProps) {
  const equityData = {
    labels: Array.from({ length: equity.length }, (_, i) => i),
    datasets: [
      {
        label: 'Equity Curve',
        data: equity,
        fill: true,
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
        tension: 0.4
      }
    ]
  };

  const drawdownData = {
    labels: Array.from({ length: drawdown.length }, (_, i) => i),
    datasets: [
      {
        label: 'Drawdown',
        data: drawdown.map(d => d * 100),
        fill: true,
        borderColor: 'rgb(255, 99, 132)',
        backgroundColor: 'rgba(255, 99, 132, 0.2)',
        tension: 0.4
      }
    ]
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">Backtest Results</h2>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
        {/* Performance Metrics */}
        <div className="bg-gray-50 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Performance Metrics</h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-gray-600">Total Trades</p>
              <p className="text-lg font-semibold">{metrics.totalTrades}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Win Rate</p>
              <p className="text-lg font-semibold text-green-600">
                {(metrics.winRate * 100).toFixed(2)}%
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Profit Factor</p>
              <p className="text-lg font-semibold">{metrics.profitFactor.toFixed(2)}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Sharpe Ratio</p>
              <p className="text-lg font-semibold">{metrics.sharpeRatio.toFixed(2)}</p>
            </div>
          </div>
        </div>

        {/* Risk Metrics */}
        <div className="bg-gray-50 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Risk Metrics</h3>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm text-gray-600">Max Drawdown</p>
              <p className="text-lg font-semibold text-red-600">
                {(metrics.maxDrawdown * 100).toFixed(2)}%
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Average Win</p>
              <p className="text-lg font-semibold text-green-600">
                ${metrics.averageWin.toFixed(2)}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Average Loss</p>
              <p className="text-lg font-semibold text-red-600">
                ${Math.abs(metrics.averageLoss).toFixed(2)}
              </p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Avg Holding Time</p>
              <p className="text-lg font-semibold">
                {metrics.averageHoldingTime.toFixed(1)}h
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Charts */}
      <div className="space-y-6">
        <div className="bg-gray-50 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Equity Curve</h3>
          <div className="h-[300px]">
            <Line
              data={equityData}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                  legend: {
                    display: false
                  },
                  tooltip: {
                    callbacks: {
                      label: (context) => `$${context.parsed.y.toFixed(2)}`
                    }
                  }
                },
                scales: {
                  y: {
                    beginAtZero: false,
                    title: {
                      display: true,
                      text: 'Equity ($)'
                    }
                  }
                }
              }}
            />
          </div>
        </div>

        <div className="bg-gray-50 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Drawdown</h3>
          <div className="h-[300px]">
            <Line
              data={drawdownData}
              options={{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                  legend: {
                    display: false
                  },
                  tooltip: {
                    callbacks: {
                      label: (context) => `${context.parsed.y.toFixed(2)}%`
                    }
                  }
                },
                scales: {
                  y: {
                    beginAtZero: true,
                    reverse: true,
                    title: {
                      display: true,
                      text: 'Drawdown (%)'
                    },
                    ticks: {
                      callback: (value) => `${value}%`
                    }
                  }
                }
              }}
            />
          </div>
        </div>
      </div>

      {/* Best/Worst Trades */}
      <div className="mt-6 bg-gray-50 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Best/Worst Trades</h3>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-gray-600">Largest Win</p>
            <p className="text-lg font-semibold text-green-600">
              ${metrics.largestWin.toFixed(2)}
            </p>
          </div>
          <div>
            <p className="text-sm text-gray-600">Largest Loss</p>
            <p className="text-lg font-semibold text-red-600">
              ${Math.abs(metrics.largestLoss).toFixed(2)}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}