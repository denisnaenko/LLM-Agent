from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

router = Router()

# обработка команды /start
@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(f'Привет! Я - твой персональный ассистент по уходу за кожей лица.\n\nЯ помогу тебе выбрать лучшие косметические средства, основываясь на их составе, а также подберу индивидуальные рекомендации по уходу за кожей.\n\nЧем могу помочь?')

# обработка команды /help
@router.message(Command('help')) 
async def get_help(message: Message):
    await message.answer("Это команда /help")

# обработка фотографий
@router.message(F.photo)
async def get_photo(message: Message):
    await message.answer(f"ID фото: {message.photo[-1].file_id}")