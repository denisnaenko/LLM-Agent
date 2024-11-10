import app.keyboards as kb
import app.database.requests as rq

from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from .skin_test import determine_skin_type



router = Router()

# создание состояние для загрузки фото
class UploadPhotoState(StatesGroup):
    waiting_for_photo = State()

# создание состояния для теста на тип кожи
class SkinTypeTest(StatesGroup):
    question_1 = State()
    question_2 = State()
    question_3 = State()
    
    calculating_result = State()


# обработка команды /start
@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await rq.set_user(message.from_user.id)
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
@router.callback_query(lambda c: c.data == "text_input")
async def text_input(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("Введите текст состава для анализа")
    await callback.answer()
    
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

# обработка опции "Персональные рекомендации" -> "Узнать свой тип кожи"
@router.callback_query(lambda c: c.data == "get_skin_type")
async def get_skin_type(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Пройдите тест, чтобы определить ваш тип кожи:")
    await callback.message.answer("Вопрос 1: Как ваша кожа реагирует на жирные кремы? (a), (b), (c)",
                                  reply_markup=kb.response_options)
    await state.set_state(SkinTypeTest.question_1)    

# обработка ответа на вопрос 1
@router.callback_query(SkinTypeTest.question_1)
async def handle_question_1(callback: CallbackQuery, state: FSMContext):
    await state.update_data(answer_1=callback.data)
    await callback.message.answer("Вопрос 2: Часто ли у вас появляются высыпания? (a), (b), (c)",
                                  reply_markup=kb.response_options)
    await state.set_state(SkinTypeTest.question_2)

# обработка ответа на вопрос 2
@router.callback_query(SkinTypeTest.question_2)
async def handle_question_2(callback: CallbackQuery, state: FSMContext):
    print(callback.data)
    await state.update_data(answer_2=callback.data)
    await callback.message.answer("Вопрос 3: Ваша кожа чувствительная? (a), (b), (c)",
                                  reply_markup=kb.response_options)
    await state.set_state(SkinTypeTest.question_3)

# обработка ответа на вопрос 3
@router.callback_query(SkinTypeTest.question_3)
async def handle_question_3(callback: CallbackQuery, state: FSMContext):
    await state.update_data(answer_3=callback.data)
    await callback.message.answer("Спасибо за ответы! Пожалуйста, подождите, пока я анализирую ваш тип кожи...")
    await state.set_state(SkinTypeTest.calculating_result)
                                  
    # получение данных из состояния
    user_data = await state.get_data()
    skin_type = determine_skin_type(user_data)

    # сохранение результата в бд
    await rq.set_skin_type(callback.from_user.id, skin_type)

    # завершение теста
    await callback.message.answer(f'Ваш тип кожи: {skin_type}')
    await state.clear()

# обработка опции "Персональные рекомендации" -> "Получить рекомендации"
@router.callback_query(lambda c: c.data == "get_recommendations")
async def get_recommendations(callback: CallbackQuery):
    await callback.message.answer("Вот персональные рекомендации для ухода за вашим типом кожи:")
    """
    (место для реализации функционала)
    ...
    """
    await callback.answer()

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

# обработка команды /help
@router.message(Command('help')) 
async def get_help(message: Message):
    await message.answer("Это команда /help")