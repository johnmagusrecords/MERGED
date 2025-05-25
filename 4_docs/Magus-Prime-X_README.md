<p align="center">
  <img src="https://raw.githubusercontent.com/johnmagusrecords/Magus-Prime-X/main/MAGUS%20PRIME%20X%20BOT%20LOGO%20PIC.png" width="180" alt="Magus Prime X Bot"/>
  <img src="https://raw.githubusercontent.com/johnmagusrecords/Magus-Prime-X/main/PRIME%20X%20SIGNALS%20WITH%20BACKGROUND.png" width="180" alt="Prime X Signals"/>
  <img src="https://raw.githubusercontent.com/johnmagusrecords/Magus-Prime-X/main/PRIME%20X%20NEWS%20WITH%20BACKGROUND.png" width="180" alt="Prime X News"/>
  <img src="https://raw.githubusercontent.com/johnmagusrecords/Magus-Prime-X/main/MAGUS%20PRIME%20APP%20LOGO%20PNG.png" width="180" alt="Magus Prime X App"/>
</p>

# MAGUS PRIME X

A professional, automated trading and signal bot for Capital.com, Forex, Crypto, Commodities, and Indices.  
Supports advanced risk management, multi-language (English/Arabic) signal formatting, Telegram integration, and news monitoring.

---

## Project Structure

| File/Folder              | Purpose                                                         |
|--------------------------|-----------------------------------------------------------------|
| `bot.py`                 | Main bot logic, Flask API, Telegram integration, trading loop    |
| `config.py`              | Loads environment/configuration, asset settings, toggles         |
| `assets_config.json`     | Per-symbol asset configuration (type, strategy, timeframe, etc.) |
| `signal_formatter.py`    | Formats signals (English/Arabic) for Telegram                   |
| `signal_dispatcher.py`   | Handles signal dispatch logic                                   |
| `enhanced_signal_sender.py` | Advanced signal sending, buttons, commentary, etc.           |
| `telegram_utils.py`      | Telegram helpers, notifications, message formatting             |
| `capital_com_trader.py`  | Capital.com API integration, trade execution                    |
| `news_monitor.py`        | News fetching, RSS/NewsAPI integration                          |
| `openai_assistant.py`    | AI commentary and GPT integration                               |
| `commentary_generator.py`| Fallback/AI commentary generation                               |
| `requirements.txt`       | Python dependencies                                             |
| `.env`                   | Environment variables (tokens, keys, chat IDs, etc.)            |
| `README.md`              | Documentation you're reading now 😉                              |
| ...other files...        | Utilities, logs, test scripts, etc.                             |

---

## Key Features

- **Modular Asset Configuration:**  
  All traded symbols and their settings are in `assets_config.json`.

- **Multi-language Signal Formatting:**  
  Signals are formatted in both English and Arabic using `signal_formatter.py`.

- **Professional Telegram Integration:**  
  - Sends signals, news, and status updates to multiple Telegram groups/chats.
  - Inline execution buttons and approval/cancel flows.
  - Startup/shutdown/status messages (🟢 BOT STARTING, 🔴 BOT STOPPED, etc).

- **News Monitoring:**  
  - Fetches news from RSS and NewsAPI.
  - Sends news to a dedicated Telegram news group.

- **Advanced Risk Management:**  
  - Per-strategy risk, daily loss/profit limits, and trade logging.
  - Configurable via `.env` and `config.py`.

- **AI Commentary:**  
  - Generates trade commentary using OpenAI GPT or fallback logic.

- **Flask API & Dashboard:**  
  - REST endpoints for stats, dashboard, and project tracker.

- **Async & Threaded Architecture:**  
  - Flask runs in a background thread.
  - Trading and news jobs scheduled asynchronously.

---

## Setup

1. **Clone the repo and install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

2. **Configure environment variables in `.env`:**
   ```
   TELEGRAM_BOT_TOKEN=...
   TELEGRAM_CHAT_ID=...
   TELEGRAM_SIGNAL_CHAT_ID=...
   TELEGRAM_NEWS_CHAT_ID=...
   CAPITAL_API_KEY=...
   CAPITAL_API_PASSWORD=...
   CAPITAL_API_IDENTIFIER=...
   NEWS_API_KEY=...
   # ...other keys as needed
   ```

3. **Edit `assets_config.json`** to match your traded symbols and strategies.

4. **Run the bot:**
   ```sh
   python bot.py
   ```

---

## Signal Formatting Example

Signals are formatted using `signal_formatter.py`:

**English:**
```
🔔 MAGUS PRIME X SIGNAL 🔔

🗓️ 2024-06-01 🕒 13:00  
💹 Asset: XAUUSD (Gold)  
📈 Strategy: Breakout  
⏳ Timeframe: 1h  
🎯 Targets:
  • TP1: 2350.0 (100 pips)
  • TP2: 2360.0 (200 pips)
  • TP3: 2370.0 (300 pips)
🔻 Stop‑Loss: 2330.0

💡 Rationale: Gold is breaking out of resistance.
```

**Arabic:**
```
🔔 إشارة MAGUS PRIME X 🔔

🗓️ 2024-06-01 🕒 13:00  
💹 الأصل: XAUUSD (الذهب)  
📈 الاستراتيجية: اختراق  
⏳ الإطار الزمني: ساعة  
🎯 الأهداف:
  • TP1: 2350.0 (+100 نقطة)
  • TP2: 2360.0 (+200 نقطة)
  • TP3: 2370.0 (+300 نقطة)
🔻 الوقف‑خسارة: 2330.0

💡 السبب: الذهب يخترق المقاومة.
```

---

## News Delivery

- News is fetched from multiple sources and sent to the group specified by `TELEGRAM_NEWS_CHAT_ID`.
- Test delivery with `prime_x_news_group_test.py`.

---

## Professional Status Messages

- On startup: `🟢 BOT STARTING` (with config summary)
- On shutdown: `🔴 BOT STOPPED` (with uptime)
- On error: `❌ Startup failed: ...`
- Periodic stats: `📊 *Bot Stats* ...`

---

## Development & Testing

- Use `prime_x_news_group_test.py` to verify news group delivery.
- All async jobs and Flask run in background threads for reliability.
- Use `.vscode/settings.json` for recommended VS Code Python settings.

---

## Contributing

Pull requests and issues are welcome!

---

## License

MIT (see LICENSE file)

---
