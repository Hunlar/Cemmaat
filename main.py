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

# === Ortam Değişkenleri ve Ayarlar === #
BOT_TOKEN = os.getenv("BOT_TOKEN")
OWNER_IDS = os.getenv("OWNER_IDS", "").split(",")

# === Loglama === #
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# === Gruba girenleri kaydetmek için === #
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
