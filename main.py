import asyncio
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from bot.handlers import register_handlers
from logger import logger

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    register_handlers(dp, bot)
    logger.info("Бот запущен")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
