```python
from datetime import datetime
from zoneinfo import ZoneInfo

# --- Config: replace these with your own strategy's real values ---
ENTRY_ALLOWED_DAYS = {2, 4}          # weekday() values: Wednesday, Friday
ENTRY_WINDOW_START = "09:45"
ENTRY_WINDOW_END = "12:15"
MAX_ENTRY_ATTEMPTS = 40
CASH_PER_TRADE = 3000                # dollars reserved per position
VIX_LOW_THRESHOLD = 20
DTE_LOW_RANGE = (20, 50)
DTE_HIGH_RANGE = (51, 90)


def format_dte_line(vix_value):
    """
    Show both DTE (days-to-expiration) ranges and bold-underline whichever
    one is actually in effect for the given VIX reading.
    """
    low_range = f"{DTE_LOW_RANGE[0]}-{DTE_LOW_RANGE[1]}"
    high_range = f"{DTE_HIGH_RANGE[0]}-{DTE_HIGH_RANGE[1]}"

    # No VIX reading yet (e.g. data feed hasn't updated) — show both ranges
    # with neither marked as selected.
    if not isinstance(vix_value, (int, float)):
        return (f"Volatility: VIX unavailable -> DTE Range: {low_range} if VIX < {VIX_LOW_THRESHOLD} "
                f"| {high_range} if VIX >= {VIX_LOW_THRESHOLD}")
    # Low-volatility regime: use the shorter/wider DTE range.
    if vix_value < VIX_LOW_THRESHOLD:
        return (f"Volatility: VIX {vix_value:.2f} -> DTE Range: __**{low_range} selected**__ "
                f"| {high_range} if VIX >= {VIX_LOW_THRESHOLD}")
    # High-volatility regime: use the narrower DTE range.
    return (f"Volatility: VIX {vix_value:.2f} -> DTE Range: {low_range} if VIX < {VIX_LOW_THRESHOLD} "
            f"| __**{high_range} selected**__")


def get_block_reasons(now, market_open, is_eligible_day, has_open_position,
                       account_cash, trend, vix_is_numeric):
    """
    Return a list of human-readable reasons an entry won't be attempted
    today. Empty list means nothing is blocking entry.
    """
    # Already-open position overrides every other reason — nothing else
    # matters if we're not flat.
    if has_open_position:
        return ["Already in an open position."]

    reasons = []
    if not market_open:
        reasons.append("Market is closed.")
    if not is_eligible_day:
        reasons.append(f"{now.strftime('%A')} is not an allowed entry day.")
    if account_cash < CASH_PER_TRADE:
        reasons.append(f"Insufficient cash. Need ${CASH_PER_TRADE:,.0f} minimum, currently ${account_cash:,.2f}.")
    if trend == "UNKNOWN":
        reasons.append("Trend signal is unknown.")
    if not vix_is_numeric:
        reasons.append("VIX data is unavailable.")
    return reasons


def get_next_step(trading_allowed, has_open_position, block_reasons):
    """Pick the single "what happens next" line shown at the bottom of the alert."""
    if has_open_position:
        return "Monitor open position. No entry attempt today."
    if trading_allowed:
        return f"Waiting for {ENTRY_WINDOW_START} entry check."
    if any("not an allowed entry day" in r for r in block_reasons):
        return "Waiting for next allowed entry day."
    return "Standing down for today."


def format_open_positions(open_positions):
    """Render the current open positions as a short multi-line block, or 'None'."""
    if not open_positions:
        return "Open Positions: None"
    lines = ["Open Positions:"]
    for pos in open_positions:
        lines.append(
            f"{pos['symbol']} {pos['expiration']} | {pos['dte']} DTE | "
            f"{pos['strategy']} | {pos['contracts']} contract(s)"
        )
    return "\n".join(lines)


def build_market_open_message(symbol, trend, vix_value, account_cash, account_equity,
                               open_positions, this_week_attempts, last_week_attempts, now):
    """
    Assemble the full "market open" Discord alert text: whether an entry is
    allowed today (and why not, if blocked), an account snapshot, current
    open positions, and the weekly attempt counter.
    """
    is_eligible_day = now.weekday() in ENTRY_ALLOWED_DAYS
    market_open = True  # plug in your own market-hours check
    has_open_position = len(open_positions) > 0
    vix_is_numeric = isinstance(vix_value, (int, float))

    # All conditions must hold for an entry attempt to be made today.
    trading_allowed = (
        is_eligible_day
        and market_open
        and not has_open_position
        and account_cash >= CASH_PER_TRADE
        and trend != "UNKNOWN"
        and vix_is_numeric
    )
    entry_today = "YES" if trading_allowed else "NO"

    block_reasons = get_block_reasons(now, market_open, is_eligible_day, has_open_position,
                                       account_cash, trend, vix_is_numeric)
    # Only insert a "Reason:" line when something is actually blocking entry.
    reason_line = f"\nReason: {'; '.join(block_reasons)}\n" if block_reasons else "\n"

    strategy = "Bull Put Spread" if trend == "UP" else "Bear Call Spread" if trend == "DOWN" else "TBD"
    positions_available = int(account_cash) // CASH_PER_TRADE
    next_line = get_next_step(trading_allowed, has_open_position, block_reasons)
    # MAX_ENTRY_ATTEMPTS of 0/None means "no cap" — display as infinity symbol.
    attempts_limit = MAX_ENTRY_ATTEMPTS or '∞'

    # .replace(' 0', ' ') strips the leading zero strftime adds to single-digit
    # hours/days (e.g. "Jul 06 08:30" -> "Jul 6 8:30") for a cleaner alert.
    return f"""MARKET OPEN | {now.strftime("%b %d %H:%M %Z").replace(' 0', ' ')}

Status: Market {'OPEN' if market_open else 'CLOSED'} | Entry Today {entry_today}{reason_line}
Account: ${account_equity:,.2f} equity | ${account_cash:,.2f} cash | Can enter {positions_available} spreads
Trend: {symbol} {trend} -> Strategy: {strategy}
{format_dte_line(vix_value)}
Entry Window: {ENTRY_WINDOW_START}-{ENTRY_WINDOW_END} {now.tzname()}

{format_open_positions(open_positions)}

Attempts: This week {this_week_attempts}/{attempts_limit} | Last week {last_week_attempts}/{attempts_limit}
Next: {next_line}"""


if __name__ == "__main__":
    mock_now = datetime(2026, 7, 8, 9, 45, tzinfo=ZoneInfo("America/Chicago"))  # a Wednesday

    message = build_market_open_message(
        symbol="VOO",
        trend="UP",
        vix_value=31.75,
        account_cash=51200.00,
        account_equity=52340.18,
        open_positions=[],
        this_week_attempts=12,
        last_week_attempts=38,
        now=mock_now,
    )
    print(message)
```
