# Discord Alerts Template

Small, reusable pieces for wiring an automated trading bot up to Discord —
alert routing plus a sample "market open" status message you can adapt to
your own strategy.

## What's in here
- `discord_alert_router.py` — routes different alert types (entries, exits,
  errors, reports) to their own Discord webhook, so you can split channels
  instead of dumping everything into one feed.
- `morning_alert.py` — builds a formatted daily "market open" readiness
  message: is trading allowed today (and why not, if blocked), account
  snapshot, open positions, and a weekly attempt counter.
- `EXAMPLE_OUTPUT.md` — a sample rendered alert with mock data so you can
  see the format without running anything.

## Requirements
- Python 3.9+
- `requests` (`pip install requests`)
- One or more Discord webhook URLs (Server Settings → Integrations → Webhooks)

## Quick start
1. Create a Discord webhook per alert channel you want (entry, exit, error, reports, etc.).
2. Set them as environment variables:
   ```
   export DISCORD_WEBHOOK_ENTRY="https://discord.com/api/webhooks/..."
   export DISCORD_WEBHOOK_ERROR="https://discord.com/api/webhooks/..."
   ```
3. Send an alert:
   ```python
   from discord_alert_router import send_discord_alert
   send_discord_alert("entry", "New position opened.")
   ```
4. Run `python morning_alert.py` to print a mock "market open" alert to your
   terminal, then wire `build_market_open_message()` into your own scheduler.

## Config (in `morning_alert.py`)
| Constant | Meaning |
|---|---|
| `ENTRY_ALLOWED_DAYS` | Which weekdays entries are allowed |
| `ENTRY_WINDOW_START` / `END` | Time window entries are checked |
| `MAX_ENTRY_ATTEMPTS` | Weekly cap on entry attempts (0/None = unlimited) |
| `CASH_PER_TRADE` | Dollars reserved per position |
| `VIX_LOW_THRESHOLD` | VIX cutoff between the two DTE ranges |
| `DTE_LOW_RANGE` / `DTE_HIGH_RANGE` | Days-to-expiration ranges per volatility regime |

All values above are placeholders — swap in whatever matches your own strategy.

## License
MIT — use it, modify it, no warranty.
