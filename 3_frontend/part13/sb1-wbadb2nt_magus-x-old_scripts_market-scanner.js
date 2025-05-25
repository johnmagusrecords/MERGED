import { capitalApi } from '../src/utils/capitalApi';
import { MarketAnalyzer } from '../src/services/MarketAnalyzer';
import { TechnicalAnalyzer } from '../src/services/analysis/TechnicalAnalyzer';
import { VolumeAnalyzer } from '../src/services/analysis/VolumeAnalyzer';
import { TelegramService } from '../src/services/TelegramService';

const marketAnalyzer = new MarketAnalyzer();
const technicalAnalyzer = new TechnicalAnalyzer();
const volumeAnalyzer = new VolumeAnalyzer();
const telegram = new TelegramService();

async function scanMarkets() {
  try {
    const symbols = JSON.parse(process.env.VITE_SYMBOLS);
    const opportunities = [];

    for (const symbol of symbols) {
      const marketData = await capitalApi.getCandles(symbol, '15m', '100');
      
      const [technical, volume, structure] = await Promise.all([
        technicalAnalyzer.analyze(marketData),
        volumeAnalyzer.analyzeVolume(marketData),
        marketAnalyzer.detectMarketStructure(marketData)
      ]);

      const opportunity = analyzeOpportunity(symbol, technical, volume, structure);
      
      if (opportunity) {
        opportunities.push(opportunity);
        await sendOpportunityAlert(opportunity);
      }
    }

    console.log(`Scan complete. Found ${opportunities.length} opportunities`);
  } catch (error) {
    console.error('Error scanning markets:', error);
  }
}

function analyzeOpportunity(symbol, technical, volume, structure) {
  // Combine analysis results to find opportunities
  const signals = [];

  // Technical Analysis Signals
  if (technical.strength > 0.7) {
    signals.push({
      type: technical.direction,
      source: 'technical',
      strength: technical.strength
    });
  }

  // Volume Analysis Signals
  if (volume.orderFlow.delta > volume.orderFlow.threshold) {
    signals.push({
      type: volume.orderFlow.delta > 0 ? 'BUY' : 'SELL',
      source: 'volume',
      strength: Math.abs(volume.orderFlow.delta) / volume.orderFlow.threshold
    });
  }

  // Market Structure Signals
  if (structure.breakoutPoints.length > 0) {
    const lastBreakout = structure.breakoutPoints[structure.breakoutPoints.length - 1];
    signals.push({
      type: lastBreakout.direction,
      source: 'structure',
      strength: lastBreakout.strength
    });
  }

  // Validate signals
  if (signals.length >= 2) {
    const avgStrength = signals.reduce((sum, s) => sum + s.strength, 0) / signals.length;
    const direction = signals[0].type; // Use first signal's direction

    if (avgStrength > 0.7 && signals.every(s => s.type === direction)) {
      return {
        symbol,
        type: direction,
        signals,
        strength: avgStrength,
        timestamp: new Date()
      };
    }
  }

  return null;
}

async function sendOpportunityAlert(opportunity) {
  const message = `
🎯 Market Opportunity Detected

Symbol: ${opportunity.symbol}
Direction: ${opportunity.type}
Strength: ${(opportunity.strength * 100).toFixed(1)}%

Signals:
${opportunity.signals.map(s => `- ${s.source.toUpperCase()}: ${(s.strength * 100).toFixed(1)}%`).join('\n')}

Time: ${opportunity.timestamp.toLocaleString()}
`;

  await telegram.sendMessage(message);
}

// Run market scanner every minute
setInterval(scanMarkets, 60 * 1000);
scanMarkets();