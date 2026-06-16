"""
Telegram bot that extracts EXIF metadata from received photos
and forwards it to a remote server via HTTP POST.

Configuration (environment variables or .env file):
    BOT_TOKEN   – Telegram Bot API token (required)
    SERVER_URL  – URL to POST metadata to (required)
    LOG_LEVEL   – logging level, default INFO
"""

import io
import logging
import os

import exifread
import requests
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

load_dotenv()

BOT_TOKEN: str = os.environ["BOT_TOKEN"]
SERVER_URL: str = os.environ["SERVER_URL"]
LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()
MAX_DISPLAYED_TAGS: int = 20
SERVER_REQUEST_TIMEOUT: int = 10

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=getattr(logging, LOG_LEVEL, logging.INFO),
)
logger = logging.getLogger(__name__)


def extract_exif(image_bytes: bytes) -> dict:
    """Return a dict of EXIF tag names to their string values using exifread."""
    try:
        tags = exifread.process_file(
            io.BytesIO(image_bytes),
            details=False,
            builtin_types=True,
        )
    except Exception as exc:
        logger.warning("Could not parse EXIF data: %s", exc)
        return {}

    metadata: dict = {}
    for tag_name, value in tags.items():
        if isinstance(value, bytes):
            value = value.decode("utf-8", errors="replace")
        metadata[tag_name] = str(value)

    return metadata


def format_metadata_summary(metadata: dict) -> str:
    """Return a Markdown-formatted summary of *metadata* for display to the user."""
    if not metadata:
        return "_Метаданных не найдено_"
    items = list(metadata.items())
    summary = "\n".join(f"• *{k}*: `{v}`" for k, v in items[:MAX_DISPLAYED_TAGS])
    if len(items) > MAX_DISPLAYED_TAGS:
        summary += f"\n…и ещё {len(items) - MAX_DISPLAYED_TAGS} тег(ов)"
    return summary


def send_to_server(payload: dict) -> requests.Response:
    """POST *payload* as JSON to SERVER_URL with a reasonable timeout."""
    response = requests.post(
        SERVER_URL,
        json=payload,
        timeout=SERVER_REQUEST_TIMEOUT,
        headers={"Content-Type": "application/json"},
    )
    response.raise_for_status()
    return response


# ---------------------------------------------------------------------------
# Telegram handlers
# ---------------------------------------------------------------------------

async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "👋 Привет! Отправь мне фотографию, и я извлеку из неё метаданные (EXIF)."
    )


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Download the best-quality photo, extract EXIF, send to server."""
    message = update.message

    # Telegram sends several sizes; pick the largest one
    photo = message.photo[-1]
    file = await context.bot.get_file(photo.file_id)

    # Download photo bytes
    buf = io.BytesIO()
    await file.download_to_memory(buf)
    image_bytes = buf.getvalue()

    metadata = extract_exif(image_bytes)

    # Build payload
    payload = {
        "telegram_user_id": message.from_user.id,
        "telegram_username": message.from_user.username or "",
        "chat_id": message.chat_id,
        "message_id": message.message_id,
        "file_id": photo.file_id,
        "file_unique_id": photo.file_unique_id,
        "exif": metadata,
    }

    logger.info("Extracted %d EXIF tag(s) for file_id=%s", len(metadata), photo.file_id)

    # Forward metadata to server
    try:
        resp = send_to_server(payload)
        logger.info("Server responded %s for file_id=%s", resp.status_code, photo.file_id)
        await message.reply_text(
            f"✅ Метаданные отправлены на сервер.\n\n{format_metadata_summary(metadata)}",
            parse_mode="Markdown",
        )
    except requests.RequestException as exc:
        logger.error("Failed to send metadata to server: %s", exc)
        await message.reply_text(
            "⚠️ Метаданные извлечены, но не удалось отправить их на сервер. "
            "Попробуйте позже."
        )


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle photos sent as documents (uncompressed originals)."""
    doc = update.message.document
    if not doc.mime_type or not doc.mime_type.startswith("image/"):
        await update.message.reply_text(
            "ℹ️ Пожалуйста, отправьте изображение (JPEG, PNG, TIFF…)."
        )
        return

    file = await context.bot.get_file(doc.file_id)
    buf = io.BytesIO()
    await file.download_to_memory(buf)
    image_bytes = buf.getvalue()

    metadata = extract_exif(image_bytes)

    payload = {
        "telegram_user_id": update.message.from_user.id,
        "telegram_username": update.message.from_user.username or "",
        "chat_id": update.message.chat_id,
        "message_id": update.message.message_id,
        "file_id": doc.file_id,
        "file_unique_id": doc.file_unique_id,
        "mime_type": doc.mime_type,
        "exif": metadata,
    }

    logger.info(
        "Extracted %d EXIF tag(s) from document file_id=%s", len(metadata), doc.file_id
    )

    try:
        resp = send_to_server(payload)
        logger.info("Server responded %s for document file_id=%s", resp.status_code, doc.file_id)
        await update.message.reply_text(
            f"✅ Метаданные отправлены на сервер.\n\n{format_metadata_summary(metadata)}",
            parse_mode="Markdown",
        )
    except requests.RequestException as exc:
        logger.error("Failed to send metadata to server (document): %s", exc)
        await update.message.reply_text(
            "⚠️ Метаданные извлечены, но не удалось отправить их на сервер. "
            "Попробуйте позже."
        )


def main() -> None:
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(MessageHandler(filters.Document.IMAGE, handle_document))

    logger.info("Bot is running. Press Ctrl+C to stop.")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
