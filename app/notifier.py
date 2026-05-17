import os
import requests
from app.models import SearchResult


def send_telegram(message: str) -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        print("Telegram not configured, skipping notification.")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown",
    }
    requests.post(url, json=payload)


def build_message(result: SearchResult) -> str:
    top = result.combinations[:3]
    lines = [f"🛫 *Watchfare Alert* — best price: *R$ {result.best_price:.0f}*\n"]

    for i, c in enumerate(top, 1):
        lines.append(
            f"{i}. R$ {c.total:.0f} | "
            f"Out: {c.outbound_date} ({c.outbound.airline}) | "
            f"Back: {c.return_date} ({c.inbound.airline})"
        )

    lines.append("\nBook at: https://www.google.com/travel/flights")
    return "\n".join(lines)


def notify(result: SearchResult) -> None:
    if not result.below_target:
        return
    message = build_message(result)
    send_telegram(message)