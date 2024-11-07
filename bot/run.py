import asyncio
import logging
import os

from aiogram import Bot, Dispatcher, F
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

# обработка фотографий
@dp.message(F.photo)
async def get_photo(message: Message):
    await message.answer(f"ID фото: {message.photo[-1].file_id}")


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())

