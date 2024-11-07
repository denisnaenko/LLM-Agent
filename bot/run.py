import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from dotenv import load_dotenv

# загружаем токен из .env
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")


bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# обработка команды /start
@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer('Бот запущен!')

# обработка команды /help
@dp.message(Command('help')) 
async def get_help(message: Message):
    await message.answer("Это команда /help")


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())

