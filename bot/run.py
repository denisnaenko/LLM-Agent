import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message
from dotenv import load_dotenv

# загружаем токен из .env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")


bot = Bot(token = BOT_TOKEN)
dp = Dispatcher()

# обработка команды /start
@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer('Бот запущен!')

async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())

