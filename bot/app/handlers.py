import app.keyboards as kb

from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery


router = Router()

# создание состояние для загрузки фото
class UploadPhotoState(StatesGroup):
    waiting_for_photo = State()

# обработка команды /start
@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(f'Привет! Я - твой персональный ассистент по уходу за кожей лица.\n\nЯ помогу тебе выбрать лучшие косметические средства, основываясь на их составе, а также подберу индивидуальные рекомендации по уходу за кожей.\n\nЧем могу помочь?',
                         reply_markup=kb.main_menu)

# обработка опции "Начать анализ"
@router.message(lambda message: message.text == "Начать анализ")
async def start_analysis(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Выберите действие для анализа состава:", reply_markup=kb.analysis_menu)

# обработка опции "Начать анализ" -> "Загрузить фото состава"
@router.callback_query(lambda c: c.data == "upload_photo")
async def upload_photo(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Загрузите фото состава для анализа")
    await state.set_state(UploadPhotoState.waiting_for_photo)
    await callback.answer()

# обработка загруженного фото в состоянии 'waiting_for_photo'
@router.message(UploadPhotoState.waiting_for_photo, F.photo)
async def handle_photo(message: Message, state: FSMContext):
    await message.answer("Функционал анализа фото ещё не реализован")
    await state.clear()

# обработка опции "Начать анализ" -> "Использовать текстовый ввод"

# обработка перехода на другие опции с 'Начать анализ' и сброс состояния
@router.message(F.text)
async def handle_other_commands(message: Message, state: FSMContext):
    await state.clear()
    if message.text == "Персональные рекомендации":
        await personal_rec(message)
    elif message.text == "История анализов":
        await analysis_history(message)
    elif message.text == "Настройки":
        await settings(message)

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