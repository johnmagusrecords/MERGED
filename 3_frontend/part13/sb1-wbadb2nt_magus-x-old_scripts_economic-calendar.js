import fetch from 'node-fetch';
import { ForexFactory } from 'forex-factory-api';
import { InvestingCom } from 'investing-com-api';

const forexFactory = new ForexFactory();
const investingCom = new InvestingCom();

async function sendTelegramMessage(message) {
  try {
    const response = await fetch(`${process.env.VITE_SUPABASE_URL}/functions/v1/telegram/send`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${process.env.VITE_SUPABASE_ANON_KEY}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ message })
    });

    if (!response.ok) {
      throw new Error('Failed to send telegram message');
    }
  } catch (error) {
    console.error('Telegram service error:', error);
    throw error;
  }
}

async function fetchEconomicEvents() {
  try {
    // Fetch events from multiple sources
    const [ffEvents, icEvents] = await Promise.all([
      forexFactory.getCalendar(),
      investingCom.getEconomicCalendar()
    ]);

    // Combine and deduplicate events
    const events = mergeEvents(ffEvents, icEvents);

    // Filter high-impact events
    const highImpactEvents = events.filter(event => event.impact === 'high');

    // Send alerts for upcoming high-impact events
    await sendEventAlerts(highImpactEvents);

    console.log('Economic calendar updated successfully');
  } catch (error) {
    console.error('Error fetching economic events:', error);
  }
}

function mergeEvents(ffEvents, icEvents) {
  const merged = [...ffEvents];
  
  // Add non-duplicate events from investing.com
  icEvents.forEach(icEvent => {
    const isDuplicate = merged.some(ffEvent => 
      ffEvent.title === icEvent.title && 
      ffEvent.date === icEvent.date
    );
    
    if (!isDuplicate) {
      merged.push(icEvent);
    }
  });

  return merged.sort((a, b) => new Date(a.date) - new Date(b.date));
}

async function sendEventAlerts(events) {
  const now = new Date();
  const upcoming = events.filter(event => {
    const eventTime = new Date(event.date);
    const timeDiff = eventTime.getTime() - now.getTime();
    return timeDiff > 0 && timeDiff < 30 * 60 * 1000; // Within next 30 minutes
  });

  for (const event of upcoming) {
    const message = formatEventAlert(event);
    await sendTelegramMessage(message);
  }
}

function formatEventAlert(event) {
  return `
🗓 Upcoming High-Impact Event

${event.title}
Time: ${event.time}
Impact: HIGH
Currency: ${event.currency}
Forecast: ${event.forecast}
Previous: ${event.previous}

⚠️ Consider closing positions affected by ${event.currency}
`;
}

// Run calendar updates every 5 minutes
setInterval(fetchEconomicEvents, 5 * 60 * 1000);
fetchEconomicEvents();