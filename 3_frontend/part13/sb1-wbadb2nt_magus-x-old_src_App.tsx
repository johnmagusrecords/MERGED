import React from 'react';
import { Activity } from 'lucide-react';
import Dashboard from './components/Dashboard';

function App() {
  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <header className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8 flex justify-between items-center">
          <div className="flex items-center space-x-3">
            <Activity className="h-8 w-8 text-indigo-600" />
            <h1 className="text-2xl font-bold text-gray-900">MAGUS PRIME X</h1>
          </div>
          <div className="flex items-center space-x-4">
            <div className="px-3 py-1 rounded-full bg-green-100 text-green-800">
              Bot Active
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-8">
        <Dashboard />
      </main>

      {/* Footer */}
      <footer className="bg-white border-t mt-auto">
        <div className="max-w-7xl mx-auto px-4 py-4 sm:px-6 lg:px-8">
          <p className="text-sm text-gray-500 text-center">
            © 2024 MAGUS PRIME X. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;