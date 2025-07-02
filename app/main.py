# app/main.py (ФИНАЛЬНАЯ ВЕРСИЯ)

import asyncio
import os
from dotenv import load_dotenv
from fastapi import FastAPI

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties # <-- ДОБАВЛЕН ЭТОТ ИМПОРТ
from aiogram.fsm.storage.memory import MemoryStorage

from app.database import engine
from app.models import Base
from bot.handlers import router as bot_router

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

# --- FastAPI App ---
app = FastAPI(title="Student Helper API")

@app.get("/")
async def root():
    return {"status": "ok", "message": "API is running"}

# --- Aiogram Bot ---
async def start_bot():
    # ИЗМЕНЕНА СТРОКА НИЖЕ
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
    
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    dp.include_router(bot_router)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


async def main():
    print("Starting bot...")
    await start_bot()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Bot stopped.")