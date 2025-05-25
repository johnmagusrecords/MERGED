import React from 'react';
import { Activity, Clock, Signal, Database, AlertTriangle } from 'lucide-react';

interface SystemStatusProps {
  uptime: number;
  lastPing: Date;
  status: 'online' | 'offline';
  apiLatency: number;
  memoryUsage: number;
  alerts: string[];
}

export default function SystemStatus({
  uptime,
  lastPing,
  status,
  apiLatency,
  memoryUsage,
  alerts
}: SystemStatusProps) {
  const formatUptime = (ms: number): string => {
    const seconds = Math.floor(ms / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);

    return `${days}d ${hours % 24}h ${minutes % 60}m`;
  };

  return (
    <div className="bg-white rounded-lg shadow-lg p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-gray-900">System Status</h2>
        <div className={`px-3 py-1 rounded-full flex items-center ${
          status === 'online' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
        }`}>
          <Activity className="w-4 h-4 mr-2" />
          {status === 'online' ? 'Online' : 'Offline'}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="space-y-4">
          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div className="flex items-center">
              <Clock className="w-5 h-5 text-gray-500 mr-3" />
              <span className="text-sm font-medium text-gray-700">Uptime</span>
            </div>
            <span className="text-sm font-semibold text-gray-900">
              {formatUptime(uptime)}
            </span>
          </div>

          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div className="flex items-center">
              <Signal className="w-5 h-5 text-gray-500 mr-3" />
              <span className="text-sm font-medium text-gray-700">API Latency</span>
            </div>
            <span className={`text-sm font-semibold ${
              apiLatency > 200 ? 'text-orange-600' : 'text-gray-900'
            }`}>
              {apiLatency}ms
            </span>
          </div>

          <div className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div className="flex items-center">
              <Database className="w-5 h-5 text-gray-500 mr-3" />
              <span className="text-sm font-medium text-gray-700">Memory Usage</span>
            </div>
            <span className={`text-sm font-semibold ${
              memoryUsage > 80 ? 'text-red-600' : 'text-gray-900'
            }`}>
              {memoryUsage}%
            </span>
          </div>
        </div>

        <div className="bg-gray-50 rounded-lg p-4">
          <div className="flex items-center mb-4">
            <AlertTriangle className="w-5 h-5 text-gray-500 mr-2" />
            <h3 className="text-sm font-medium text-gray-700">Recent Alerts</h3>
          </div>
          
          <div className="space-y-2 max-h-40 overflow-y-auto">
            {alerts.length > 0 ? (
              alerts.map((alert, index) => (
                <div
                  key={index}
                  className="text-sm p-2 rounded bg-white border-l-4 border-orange-500"
                >
                  {alert}
                </div>
              ))
            ) : (
              <p className="text-sm text-gray-500 italic">No recent alerts</p>
            )}
          </div>
        </div>
      </div>

      <div className="mt-6 pt-4 border-t border-gray-200">
        <div className="flex items-center justify-between text-sm text-gray-500">
          <span>Last System Check:</span>
          <span>{lastPing.toLocaleString()}</span>
        </div>
      </div>
    </div>
  );
}