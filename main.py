import os
import logging
import random
import requests
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    ContextTypes, filters
)
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# === Ortam değişkenleri === #
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_IDS = os.getenv("OWNER_IDS", "").split(",")

# === Logging === #
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# === Global grup listesi === #
joined_chats = set()

# === API Fonksiyonları === #
def fetch_random_hadis():
    try:
        response = requests.get("https://hadis-api.vercel.app/v1/hadis/random")
        if response.status_code == 200:
            data = response.json()["data"]
            hadis = data.get("hadis", "")
            kaynak = data.get("kaynak", "")
            return f"{hadis}\n({kaynak})"
    except Exception as e:
        logging.error(f"Hadis API hatası: {e}")
    return "Hadis alınamadı."

def fetch_random_ayah():
    try:
        ayet_no = random.randint(1, 6236)
        url = f"https://api.alquran.cloud/v1/ayah/{ayet_no}/tr.diyanet"
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()["data"]
            sure = data["surah"]["name"]
            ayet = data["numberInSurah"]
            text = data["text"]
            return f"{sure} Suresi {ayet}. Ayet:\n\n{text}"
    except Exception as e:
        logging.error(f"Ayet API hatası: {e}")
    return "Ayet alınamadı."

# === Komutlar === #
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Selam! Kur'an ve Hadis botuna hoş geldin. Komutlar için /help yazabilirsin."
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/start - Botu başlatır\n"
        "/help - Komutları gösterir\n"
        "/ayet - Rastgele Kur'an ayeti getirir"
    )

async def ayet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mesaj = fetch_random_ayah()
    await update.message.reply_text(mesaj)

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
    try:
        await context.bot.send_message(chat_id=chat_id, text=mesaj)
        await update.message.reply_text("Mesaj gönderildi.")
    except Exception as e:
        await update.message.reply_text(f"Hata: {e}")

async def track_groups(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if chat.type in ["group", "supergroup"]:
        joined_chats.add(chat.id)

async def send_hourly_hadis(app):
    for chat_id in joined_chats:
        try:
            hadis = fetch_random_hadis()
            await app.bot.send_message(chat_id=chat_id, text=hadis)
        except Exception as e:
            logging.warning(f"{chat_id} grubuna hadis gönderilemedi: {e}")

# === Botu başlat === #
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("ayet", ayet))
    app.add_handler(CommandHandler("hell", hell))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, track_groups))

    scheduler = AsyncIOScheduler()
    scheduler.add_job(lambda: send_hourly_hadis(app), 'cron', minute=0)
    scheduler.start()

    app.run_polling()
