import React, { useState, useEffect } from 'react';
import { Newspaper, TrendingUp, TrendingDown, AlertTriangle } from 'lucide-react';

interface NewsItem {
  title: string;
  source: string;
  timestamp: string;
  sentiment: number;
  impact: 'high' | 'medium' | 'low';
  symbols: string[];
  summary: string;
  url: string;
  language: 'en' | 'ar';
}

export default function NewsImpactAnalysis() {
  const [news, setNews] = useState<NewsItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedImpact, setSelectedImpact] = useState<'all' | 'high' | 'medium' | 'low'>('all');
  const [selectedLanguage, setSelectedLanguage] = useState<'en' | 'ar'>('en');

  useEffect(() => {
    fetchNewsData();
    const interval = setInterval(fetchNewsData, 60000); // Refresh every minute
    return () => clearInterval(interval);
  }, [selectedLanguage]);

  const fetchNewsData = async () => {
    try {
      // In production, replace with actual API call
      const mockNews: NewsItem[] = [
        {
          title: 'US CPI Data Shows Higher Than Expected Inflation',
          source: 'Reuters',
          timestamp: new Date().toISOString(),
          sentiment: -0.8,
          impact: 'high',
          symbols: ['USD', 'EURUSD', 'GBPUSD'],
          summary: 'Consumer Price Index data released today shows inflation remains elevated...',
          url: 'https://example.com/news/1',
          language: 'en'
        },
        {
          title: 'مؤشر أسعار المستهلك الأمريكي يظهر ارتفاعاً في التضخم',
          source: 'Reuters Arabic',
          timestamp: new Date().toISOString(),
          sentiment: -0.8,
          impact: 'high',
          symbols: ['USD', 'EURUSD', 'GBPUSD'],
          summary: 'أظهرت بيانات مؤشر أسعار المستهلك اليوم استمرار ارتفاع التضخم...',
          url: 'https://example.com/news/1-ar',
          language: 'ar'
        }
      ];

      setNews(mockNews.filter(item => item.language === selectedLanguage));
      setLoading(false);
    } catch (error) {
      console.error('Error fetching news data:', error);
      setLoading(false);
    }
  };

  const getSentimentColor = (sentiment: number) => {
    if (sentiment > 0.3) return 'text-green-600';
    if (sentiment < -0.3) return 'text-red-600';
    return 'text-gray-600';
  };

  const getImpactBadgeColor = (impact: string) => {
    switch (impact) {
      case 'high':
        return 'bg-red-100 text-red-800';
      case 'medium':
        return 'bg-yellow-100 text-yellow-800';
      case 'low':
        return 'bg-green-100 text-green-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const filteredNews = selectedImpact === 'all' 
    ? news 
    : news.filter(item => item.impact === selectedImpact);

  return (
    <div className="bg-white rounded-lg shadow-lg p-6" dir={selectedLanguage === 'ar' ? 'rtl' : 'ltr'}>
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-gray-900 flex items-center">
          <Newspaper className="h-5 w-5 mr-2" />
          {selectedLanguage === 'en' ? 'News Impact Analysis' : 'تحليل تأثير الأخبار'}
        </h2>
        <div className="flex space-x-2">
          <button
            onClick={() => setSelectedLanguage('en')}
            className={`px-3 py-1 rounded-md text-sm ${
              selectedLanguage === 'en' 
                ? 'bg-indigo-100 text-indigo-800' 
                : 'bg-gray-100 text-gray-600'
            }`}
          >
            English
          </button>
          <button
            onClick={() => setSelectedLanguage('ar')}
            className={`px-3 py-1 rounded-md text-sm ${
              selectedLanguage === 'ar' 
                ? 'bg-indigo-100 text-indigo-800' 
                : 'bg-gray-100 text-gray-600'
            }`}
          >
            العربية
          </button>
          <button
            onClick={() => setSelectedImpact('all')}
            className={`px-3 py-1 rounded-md text-sm ${
              selectedImpact === 'all' 
                ? 'bg-indigo-100 text-indigo-800' 
                : 'bg-gray-100 text-gray-600'
            }`}
          >
            {selectedLanguage === 'en' ? 'All' : 'الكل'}
          </button>
          <button
            onClick={() => setSelectedImpact('high')}
            className={`px-3 py-1 rounded-md text-sm ${
              selectedImpact === 'high' 
                ? 'bg-red-100 text-red-800' 
                : 'bg-gray-100 text-gray-600'
            }`}
          >
            {selectedLanguage === 'en' ? 'High Impact' : 'تأثير عالي'}
          </button>
        </div>
      </div>

      {loading ? (
        <div className="flex justify-center items-center h-40">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500"></div>
        </div>
      ) : (
        <div className="space-y-4">
          {filteredNews.map((item, index) => (
            <div key={index} className="border rounded-lg p-4 hover:bg-gray-50">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-2">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getImpactBadgeColor(item.impact)}`}>
                      {item.impact.toUpperCase()}
                    </span>
                    <span className="text-sm text-gray-500">{item.source}</span>
                    <span className="text-sm text-gray-500">
                      {new Date(item.timestamp).toLocaleString(selectedLanguage === 'en' ? 'en-US' : 'ar-SA')}
                    </span>
                  </div>
                  <h3 className="mt-2 text-lg font-medium text-gray-900">{item.title}</h3>
                  <p className="mt-1 text-sm text-gray-600">{item.summary}</p>
                  <div className="mt-2 flex flex-wrap gap-2">
                    {item.symbols.map((symbol, idx) => (
                      <span
                        key={idx}
                        className="px-2 py-1 text-xs font-medium bg-gray-100 text-gray-600 rounded-full"
                      >
                        {symbol}
                      </span>
                    ))}
                  </div>
                </div>
                <div className="ml-4 flex flex-col items-end">
                  <div className={`flex items-center ${getSentimentColor(item.sentiment)}`}>
                    {item.sentiment > 0 ? (
                      <TrendingUp className="h-5 w-5 mr-1" />
                    ) : (
                      <TrendingDown className="h-5 w-5 mr-1" />
                    )}
                    <span className="font-medium">
                      {Math.abs(item.sentiment * 100).toFixed(1)}%
                    </span>
                  </div>
                  {Math.abs(item.sentiment) > 0.7 && (
                    <div className="mt-2 flex items-center text-orange-500">
                      <AlertTriangle className="h-4 w-4 mr-1" />
                      <span className="text-xs">
                        {selectedLanguage === 'en' ? 'High Impact' : 'تأثير عالي'}
                      </span>
                    </div>
                  )}
                </div>
              </div>
              <div className="mt-3 flex justify-end">
                <a
                  href={item.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-sm text-indigo-600 hover:text-indigo-800"
                >
                  {selectedLanguage === 'en' ? 'Read More →' : '← اقرأ المزيد'}
                </a>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}