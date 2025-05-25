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
            <img 
              src="/assets/logos/mprime-logo.png" 
              alt="MAGUS PRIME X" 
              className="h-8 w-auto"
              onError={(e) => {
                // Fallback to icon if image fails to load
                e.currentTarget.style.display = 'none';
                const parent = e.currentTarget.parentElement;
                if (parent) {
                  const icon = document.createElement('span');
                  icon.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="h-8 w-8 text-indigo-600"><path d="M22 12h-4l-3 9L9 3l-3 9H2"></path></svg>';
                  parent.appendChild(icon);
                }
              }}
            />
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
            © {new Date().getFullYear()} MAGUS PRIME X. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;