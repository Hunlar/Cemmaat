# main.py

import os
import logging
import random
import requests
import asyncio
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters
)
from apscheduler.schedulers.asyncio import AsyncIOScheduler

BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_IDS = os.getenv("OWNER_IDS", "").split(",")

logging.basicConfig(level=logging.INFO)
joined_chats = set()

def fetch_random_hadis():
    try:
        response = requests.get("https://hadis-api.vercel.app/v1/hadis/random")
        if response.status_code == 200:
            data = response.json()["data"]
            return f"{data.get('hadis')}\n({data.get('kaynak')})"
    except Exception as e:
        logging.error(f"Hadis API hatası: {e}")
    return "Hadis alınamadı."

def fetch_random_ayah():
    try:
        ayet_no = random.randint(1, 6236)
        response = requests.get(f"https://api.alquran.cloud/v1/ayah/{ayet_no}/tr.diyanet")
        if response.status_code == 200:
            data = response.json()["data"]
            return f"{data['surah']['name']} Suresi {data['numberInSurah']}. Ayet:\n\n{data['text']}"
    except Exception as e:
        logging.error(f"Ayet API hatası: {e}")
    return "Ayet alınamadı."

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Selam! Kur'an ve Hadis botuna hoş geldin. /help ile komutları görebilirsin.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("/start\n/help\n/ayet")

async def ayet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(fetch_random_ayah())

async def hell(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id not in OWNER_IDS:
        await update.message.reply_text("Bu komutu kullanamazsın.")
        return
    if len(context.args) < 2:
        await update.message.reply_text("Kullanım: /hell <chat_id> <mesaj>")
        return
    chat_id = context.args[0]
    mesaj = " ".join(context.args[1:])
    await context.bot.send_message(chat_id=chat_id, text=mesaj)

async def track_groups(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if chat.type in ["group", "supergroup"]:
        joined_chats.add(chat.id)

async def send_hourly_hadis(bot_app):
    for chat_id in joined_chats:
        try:
            await bot_app.bot.send_message(chat_id=chat_id, text=fetch_random_hadis())
        except Exception as e:
            logging.warning(f"{chat_id} grubuna gönderilemedi: {e}")

# ✅ async ana fonksiyon
async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("ayet", ayet))
    app.add_handler(CommandHandler("hell", hell))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, track_groups))

    scheduler = AsyncIOScheduler()

    async def hadis_job():
        await send_hourly_hadis(app)

    scheduler.add_job(hadis_job, "cron", minute=0)
    scheduler.start()

    await app.run_polling()

# ✅ Çalıştırıcı
if __name__ == "__main__":
    asyncio.run(main())
