import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

TELEGA_TOKEN = os.getenv("TELEGA_TOKEN")
CORE_URL = os.getenv("CORE_URL", "http://localhost:8001")

if not TELEGA_TOKEN:
    raise RuntimeError("TELEGA_TOKEN не задан (см. .env)")

MAX_LEN = 4096
def chunk(text: str, n: int = MAX_LEN - 16):
    for i in range(0, len(text), n):
        yield text[i:i+n]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "UI для LLM агента приветствует Вас!"
    )

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Контекст будет очищен при следующем сообщении.")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    cid = str(update.effective_chat.id)
    text = update.message.text or ""
    payload = {"channel": "telegram", "user_id": cid, "text": text}
    try:
        r = requests.post(f"{CORE_URL}/v1/chat", json=payload, timeout=60)
        r.raise_for_status()
        data = r.json()
        parts = data.get("parts", [])
        if not parts:
            await update.message.reply_text("Core API вернул пустой ответ.")
            return
        for p in parts:
            for piece in chunk(p):
                await update.message.reply_text(piece, disable_web_page_preview=True)
    except requests.RequestException as e:
        await update.message.reply_text(f"Нет связи с Core API: {e}")
    except Exception as e:
        await update.message.reply_text(f"Ошибка: {e}")

def run():
    app = Application.builder().token(TELEGA_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("reset", reset))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))
    print(f"Telegram bot → CORE_URL={CORE_URL}")
    app.run_polling()

if __name__ == "__main__":
    run()
