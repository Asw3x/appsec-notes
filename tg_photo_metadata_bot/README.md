# Telegram Photo Metadata Bot

A Telegram bot that extracts **EXIF metadata** from photos sent by users and forwards the data to a remote server via HTTP POST.

---

## Features

- Handles compressed photos sent through Telegram (`.photo` messages).
- Handles images sent as **documents** (uncompressed originals — recommended for full EXIF preservation).
- Extracts all available EXIF tags using **Pillow**.
- Forwards a JSON payload to a configurable server endpoint.
- Replies to the user with a summary of extracted tags.

---

## Requirements

- Python 3.10+
- A Telegram bot token ([create one via @BotFather](https://t.me/BotFather))
- An HTTP endpoint that accepts `POST` requests with a JSON body

---

## Setup

```bash
# 1. Clone the repository and enter the bot directory
cd tg_photo_metadata_bot

# 2. Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env
# Edit .env and fill in BOT_TOKEN and SERVER_URL
```

---

## Configuration

| Variable    | Required | Description                                              |
|-------------|----------|----------------------------------------------------------|
| `BOT_TOKEN` | ✅ Yes   | Telegram bot token from @BotFather                       |
| `SERVER_URL`| ✅ Yes   | Full URL where metadata JSON will be POSTed              |
| `LOG_LEVEL` | No       | Logging verbosity (`DEBUG`, `INFO`, `WARNING`). Default: `INFO` |

---

## Running

```bash
python bot.py
```

Stop the bot with `Ctrl+C`.

---

## Server Payload Format

The bot sends a `POST` request with `Content-Type: application/json` to `SERVER_URL`.

**Example payload for a photo message:**

```json
{
  "telegram_user_id": 123456789,
  "telegram_username": "alice",
  "chat_id": 123456789,
  "message_id": 42,
  "file_id": "AgACAgIAAxkBAAI...",
  "file_unique_id": "AQADmbIxGw...",
  "exif": {
    "Make": "Apple",
    "Model": "iPhone 14 Pro",
    "DateTime": "2024:06:01 12:34:56",
    "GPSInfo": "...",
    "Software": "17.0"
  }
}
```

> **Note:** Telegram re-compresses photos sent as regular messages and **strips most EXIF data** (including GPS). To preserve full metadata, ask users to send images as **files** (Documents) rather than as photos.

---

## Security Notes

- Never commit your `.env` file or expose your `BOT_TOKEN`.
- Validate and sanitize all incoming payloads on the server side.
- Consider adding authentication (e.g., a shared secret header) between the bot and the server.
- Run the bot behind a process manager (e.g., `systemd`, `supervisord`, or Docker) for production use.
