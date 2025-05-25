# MAGUS PRIME X Telegram Commands

Here's a list of commands you can use to control the MAGUS PRIME X trading bot through Telegram:

## Bot Control Commands

| Command      | Description                                           |
| ------------ | ----------------------------------------------------- |
| `/pause`     | Pause the trading bot (stops new signals)             |
| `/resume`    | Resume the trading bot                                |
| `/status`    | Get current bot status, win rate, and PnL information |
| `/dashboard` | Get URL to the web dashboard                          |
| `/closeall`  | Close all open positions and exit all trades          |

## Trading Commands

| Command                       | Description                                    |
| ----------------------------- | ---------------------------------------------- |
| `/forcebuy SYMBOL [TP] [SL]`  | Force a BUY trade for the given symbol         |
| `/forcesell SYMBOL [TP] [SL]` | Force a SELL trade for the given symbol        |
| `/forceloss [SYMBOL]`         | Mark current trade as loss (or specify symbol) |
| `/signal SYMBOL`              | Check current signal for a specific symbol     |

## Recovery Mode Commands

| Command        | Description                                              |
| -------------- | -------------------------------------------------------- |
| `/recoveryon`  | Enable auto-recovery mode (sends counter-trade after SL) |
| `/recoveryoff` | Disable auto-recovery mode                               |

## Examples
