import asyncio
import os

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

# загружаем токен из .env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")


bot = Bot(token = BOT_TOKEN)
dp = Dispatcher()

async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
