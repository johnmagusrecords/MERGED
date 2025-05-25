import { NewsAPI } from 'newsapi';
import { FinancialNews } from 'financial-news-api';
import { MarketSentiment } from 'market-sentiment-analyzer';
import { TelegramService } from '../src/services/TelegramService';

const newsApi = new NewsAPI(process.env.VITE_NEWSAPI_KEY);
const financialNews = new FinancialNews();
const sentiment = new MarketSentiment();
const telegram = new TelegramService();

async function analyzeNews() {
  try {
    // Fetch news from multiple sources
    const [newsApiArticles, financialArticles] = await Promise.all([
      fetchNewsApiArticles(),
      fetchFinancialNewsArticles()
    ]);

    // Combine and analyze articles
    const articles = [...newsApiArticles, ...financialArticles];
    const analyzedArticles = await analyzeArticles(articles);

    // Filter and send high-impact news alerts
    const highImpact = analyzedArticles.filter(article => 
      Math.abs(article.sentiment) > 0.7 || article.impact === 'high'
    );

    await sendNewsAlerts(highImpact);

    console.log('News analysis completed successfully');
  } catch (error) {
    console.error('Error analyzing news:', error);
  }
}

async function fetchNewsApiArticles() {
  const response = await newsApi.v2.everything({
    q: 'forex OR cryptocurrency OR "stock market" OR commodities',
    language: process.env.VITE_NEWS_LANG,
    sortBy: 'publishedAt',
    pageSize: parseInt(process.env.VITE_NEWS_LIMIT)
  });

  return response.articles;
}

async function fetchFinancialNewsArticles() {
  return financialNews.getLatestNews({
    categories: ['forex', 'crypto', 'commodities'],
    limit: parseInt(process.env.VITE_NEWS_LIMIT)
  });
}

async function analyzeArticles(articles) {
  const analyzed = [];

  for (const article of articles) {
    const sentimentScore = await sentiment.analyze(article.title + ' ' + article.description);
    const impact = calculateNewsImpact(article, sentimentScore);

    analyzed.push({
      ...article,
      sentiment: sentimentScore,
      impact,
      symbols: extractSymbols(article)
    });
  }

  return analyzed;
}

function calculateNewsImpact(article, sentiment) {
  const importantEvents = JSON.parse(process.env.VITE_IMPORTANT_EVENTS);
  const hasHighImpactKeywords = importantEvents.some(keyword => 
    article.title.toLowerCase().includes(keyword.toLowerCase())
  );

  if (hasHighImpactKeywords || Math.abs(sentiment) > 0.8) {
    return 'high';
  } else if (Math.abs(sentiment) > 0.5) {
    return 'medium';
  }
  return 'low';
}

function extractSymbols(article) {
  const symbolRegex = /[A-Z]{3}\/[A-Z]{3}|[A-Z]{6}|BTC|ETH|XRP|USD/g;
  const matches = article.title.match(symbolRegex) || [];
  return [...new Set(matches)];
}

async function sendNewsAlerts(articles) {
  for (const article of articles) {
    const message = formatNewsAlert(article);
    await telegram.sendMessage(message);
  }
}

function formatNewsAlert(article) {
  return `
📰 High-Impact News Alert

${article.title}

Impact: ${article.impact.toUpperCase()}
Sentiment: ${(article.sentiment * 100).toFixed(1)}%
Affected Symbols: ${article.symbols.join(', ')}

${article.description}

Source: ${article.source.name}
`;
}

// Run news analysis every 5 minutes
setInterval(analyzeNews, 5 * 60 * 1000);
analyzeNews();