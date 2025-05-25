import React from 'react';
import { Brain, TrendingUp, TrendingDown } from 'lucide-react';
import { MarketSentiment as MarketSentimentType } from '../types/trading';

const mockSentiment: MarketSentimentType = {
  score: 0.7,
  trend: 'bullish',
  lastUpdated: '2024-02-29T15:30:00Z'
};

export default function MarketSentiment() {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900">Market Sentiment</h3>
        <Brain className="h-5 w-5 text-indigo-600" />
      </div>
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-600">AI Sentiment Score</span>
          <div className="flex items-center">
            {mockSentiment.trend === 'bullish' ? (
              <TrendingUp className="h-4 w-4 text-green-500 mr-2" />
            ) : (
              <TrendingDown className="h-4 w-4 text-red-500 mr-2" />
            )}
            <span className="text-sm font-medium text-gray-900">{(mockSentiment.score * 100).toFixed(1)}%</span>
          </div>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-green-500 h-2 rounded-full"
            style={{ width: `${mockSentiment.score * 100}%` }}
          ></div>
        </div>
        <div className="flex justify-between items-center pt-2">
          <span className="text-xs text-gray-500">
            Last updated: {new Date(mockSentiment.lastUpdated).toLocaleTimeString()}
          </span>
          <span className={`text-xs font-medium ${
            mockSentiment.trend === 'bullish' ? 'text-green-600' : 'text-red-600'
          }`}>
            {mockSentiment.trend.toUpperCase()}
          </span>
        </div>
      </div>
    </div>
  );
}