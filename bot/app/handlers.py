import app.keyboards as kb

from aiogram import F, Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery


router = Router()

# обработка команды /start
@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(f'Привет! Я - твой персональный ассистент по уходу за кожей лица.\n\nЯ помогу тебе выбрать лучшие косметические средства, основываясь на их составе, а также подберу индивидуальные рекомендации по уходу за кожей.\n\nЧем могу помочь?',
                         reply_markup=kb.main_menu)

# обработка опции "Начать анализ"
@router.message(lambda message: message.text == "Начать анализ")
async def start_analysis(message: Message):
    await message.answer("Выберите действие для анализа состава:", reply_markup=kb.analysis_menu)

# обработка опции "Начать анализ" -> "Загрузить фото упаковки"

# обработка опции "Начать анализ" -> "Использовать текстовый ввод"

# обработка опции "Персональные рекомендации"
@router.message(lambda message: message.text == "Персональные рекомендации")
async def personal_rec(message: Message):
    await message.answer("Выберите действие для персональных рекомендаций:", reply_markup=kb.personal_rec_menu)

# обработка опции "Персональные рекомендации" -> "Ввести данные о коже"

# обработка опции "Персональные рекомендации" -> "Получить рекомендации"

# обработка опции "История анализов"
@router.message(lambda message: message.text == "История анализов")
async def analysis_history(message: Message):
    await message.answer("Здесь будет ваша история анализов (функционал пока не реализован)")

# обработка опции "Настройки"
@router.message(lambda message: message.text == "Настройки")
async def settings(message: Message):
    await message.answer("Настройки:", reply_markup=kb.settings_menu)

# обработка опции "Настройки" -> "Обновить информацию о коже"

# обработка опции "Настройки" -> "Включить/выключить уведомления"

# обработка опции "Настройки" -> "Удалить историю анализов"

# обработка опции ... -> "Назад в меню"

# обработка команды /help
@router.message(Command('help')) 
async def get_help(message: Message):
    await message.answer("Это команда /help")