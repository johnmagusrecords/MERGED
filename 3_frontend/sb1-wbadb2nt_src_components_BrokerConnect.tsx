import React, { useState } from 'react';
import { Lock, Unlock, RefreshCw } from 'lucide-react';
import { BrokerType, BrokerCredentials } from '../types/broker';

interface BrokerConnectProps {
  onConnect: (credentials: BrokerCredentials) => Promise<boolean>;
}

export default function BrokerConnect({ onConnect }: BrokerConnectProps) {
  const [broker, setBroker] = useState<BrokerType>('capital');
  const [isConnecting, setIsConnecting] = useState(false);
  const [credentials, setCredentials] = useState<BrokerCredentials>({
    type: 'capital',
    apiKey: '',
    password: '',
    identifier: ''
  });

  const handleConnect = async () => {
    setIsConnecting(true);
    try {
      const success = await onConnect(credentials);
      if (success) {
        // Show success notification
      }
    } catch (error) {
      // Show error notification
    } finally {
      setIsConnecting(false);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-xl font-semibold mb-4">Connect Your Trading Account</h2>
      
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Select Broker
          </label>
          <select
            value={broker}
            onChange={(e) => {
              setBroker(e.target.value as BrokerType);
              setCredentials({ type: e.target.value as BrokerType });
            }}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <option value="capital">Capital.com</option>
            <option value="mt5">MetaTrader 5</option>
          </select>
        </div>

        {broker === 'capital' && (
          <>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                API Key
              </label>
              <input
                type="password"
                value={credentials.apiKey}
                onChange={(e) => setCredentials({ ...credentials, apiKey: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                API Password
              </label>
              <input
                type="password"
                value={credentials.password}
                onChange={(e) => setCredentials({ ...credentials, password: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                API Identifier
              </label>
              <input
                type="text"
                value={credentials.identifier}
                onChange={(e) => setCredentials({ ...credentials, identifier: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
          </>
        )}

        {broker === 'mt5' && (
          <>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                MT5 Token
              </label>
              <input
                type="password"
                value={credentials.token}
                onChange={(e) => setCredentials({ ...credentials, token: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Account ID
              </label>
              <input
                type="text"
                value={credentials.accountId}
                onChange={(e) => setCredentials({ ...credentials, accountId: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
          </>
        )}

        <button
          onClick={handleConnect}
          disabled={isConnecting}
          className="w-full flex items-center justify-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
        >
          {isConnecting ? (
            <>
              <RefreshCw className="animate-spin -ml-1 mr-2 h-4 w-4" />
              Connecting...
            </>
          ) : (
            <>
              <Lock className="-ml-1 mr-2 h-4 w-4" />
              Connect Account
            </>
          )}
        </button>
      </div>

      <div className="mt-4 text-xs text-gray-500">
        <p className="flex items-center">
          <Lock className="h-3 w-3 mr-1" />
          Your credentials are securely encrypted and never stored
        </p>
      </div>
    </div>
  );
}