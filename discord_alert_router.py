```python
import os
import logging
import requests

logger = logging.getLogger()

# One webhook URL per alert category, pulled from env vars so no secrets
# live in source. Add/remove keys here as you add/remove alert types.
DISCORD_WEBHOOKS = {
    "entry": os.environ.get("DISCORD_WEBHOOK_ENTRY"),
    "exit": os.environ.get("DISCORD_WEBHOOK_EXIT"),
    "error": os.environ.get("DISCORD_WEBHOOK_ERROR"),
    "reports": os.environ.get("DISCORD_WEBHOOK_REPORTS"),
}

def send_discord_alert(channel: str, message: str, username: str = "Trading Bot"):
    """
    Post a message to a Discord webhook keyed by alert category.

    channel: which entry in DISCORD_WEBHOOKS to use (e.g. "entry", "error").
    message: plain text sent as the Discord message body.
    username: display name Discord shows for the bot on this message.
    """
    # Look up the webhook URL for this channel; bail out quietly if it's
    # not configured yet instead of crashing the caller.
    webhook_url = DISCORD_WEBHOOKS.get(channel)
    if not webhook_url:
        logger.warning(f"No webhook configured for channel '{channel}'")
        return

    try:
        # Discord's webhook API expects a JSON body with at least "content";
        # a successful post returns 204 No Content.
        payload = {"content": message, "username": username}
        response = requests.post(webhook_url, json=payload, timeout=5)
        if response.status_code != 204:
            logger.warning(f"Discord alert failed ({response.status_code}): {response.text}")
    except Exception as e:
        # Never let a Discord outage take down the caller (e.g. an
        # order-placement flow) — log and move on.
        logger.error(f"Discord alert exception: {e}")
```
