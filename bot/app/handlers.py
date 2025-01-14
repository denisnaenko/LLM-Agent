import app.keyboards as kb
import app.database.requests as rq
import os

from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from .skin_test import determine_skin_type
from .services.cropper import crop_object_async
from .services.find_func import analyze_ingredients

router = Router()

# создание состояние для загрузки фото
class UploadPhotoState(StatesGroup):
    waiting_for_photo = State()

# создание состояния для теста на тип кожи
class SkinTypeTest(StatesGroup):
    question_1 = State()
    question_2 = State()
    question_3 = State()
    question_4 = State()
    question_5 = State()
    question_6 = State()
    question_7 = State()
    question_8 = State()
    question_9 = State()
    question_10 = State()
    question_11 = State()
    question_12 = State()
    question_13 = State()
    calculating_result = State()

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
    
    # Скачиваем изображение
    photo = message.photo[-1]   # берём изображение максимального разрешения

    file = await message.bot.get_file(photo.file_id)
    file_path = file.file_path

    destination = f"downloads/{photo.file_id}.jpg"
    os.makedirs("downloads", exist_ok=True)

    # Загружаем фото
    await message.bot.download_file(file_path, destination)

    # Обрезаем фото
    crooper_res, cropper_msg = await crop_object_async(destination)

    # Отправляем полученный исход обрезки фото
    await message.answer(cropper_msg)

    # Анализируем ингредиенты с фото
    if crooper_res:
        product_conclusion = await analyze_ingredients()

    await message.answer(product_conclusion)

    # удаляем временный файл
    os.remove(destination)

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

# Вопрос 1:
@router.callback_query(lambda c: c.data == "get_skin_type")
async def get_skin_type(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Пройдите тест, чтобы определить ваш тип кожи и её особенности:")
    await callback.message.answer("Вопрос 1: Какие ощущения испытывает ваша кожа после умывания?\n\nA) Дискомфорт отсутствует, кожа свежая, сияющая.\n\nB) Появляется чувство стянутости, сухость, дискомфорт.\n\nC) Уже через 20 минут после умывания появляется незначительный жирный блеск лица.\n\nD) После умывания появляется чрезмерный блеск лица в Т-зоне, область щек остается матовой.",
                                  reply_markup=kb.response_4_options)
    await state.set_state(SkinTypeTest.question_1)    

# Вопрос 2:
@router.callback_query(SkinTypeTest.question_1)
async def handle_question_1(callback: CallbackQuery, state: FSMContext):
    await state.update_data(answer_1=callback.data)
    await callback.message.answer("Вопрос 2: Какие ощущения испытывает кожа, если пренебречь этапом её увлажнения?\n\nA) Не использую увлажняющий крем, без него кожа чувствует себя отлично.\n\nB) Увлажняющий крем - незаменимый этап моей бьюти-рутины, так как без него кожа сухая и стянутая.\n\nС) Без увлажнения жирный блеск лица усиливается.\n\nD) Без увлажнения жирный блеск лица усиливается в Т-зоне, область щек остается матовой.",
                                  reply_markup=kb.response_4_options)
    await state.set_state(SkinTypeTest.question_2)

# Вопрос 3:
@router.callback_query(SkinTypeTest.question_2)
async def handle_question_2(callback: CallbackQuery, state: FSMContext):
    await state.update_data(answer_2=callback.data)
    await callback.message.answer("Вопрос 3: Свойственен ли для вашей кожи жирный блеск?\n\nA) Нет, жирный блеск отсутствует.\n\nB) Лёгкий жирный блеск появляется к концу дня.\n\nC) Да, присутствует на всем лице.\n\nD) Иногда жирный блеск появляется в Т-зоне.",
                                  reply_markup=kb.response_4_options)
    await state.set_state(SkinTypeTest.question_3)

# Вопрос 4:
@router.callback_query(SkinTypeTest.question_3)
async def handle_question_3(callback: CallbackQuery, state: FSMContext):
    await state.update_data(answer_3=callback.data)
    await callback.message.answer("Вопрос 4: Оцените состояние пор на вашем лице\n\nA) Поры незаметны, высыпания практически не появляются.\n\nB) Поры практически незаметны, высыпания появляются редко.\n\nC) Поры преимущественно расширенные, на лице имеются несовершенства: прыщи, черные точки, сыпь.\n\nD) Поры расширены только в области лба, носа и подбородка. В U-зоне пор нет или они слабозаметны.",
                                  reply_markup=kb.response_4_options)
    await state.set_state(SkinTypeTest.question_4)

# Вопрос 5:
@router.callback_query(SkinTypeTest.question_4)
async def handle_question_4(callback: CallbackQuery, state: FSMContext):
    await state.update_data(answer_4=callback.data)
    await callback.message.answer("Вопрос 5: Реагирует ли ваша кожа на влияние внешних и внутренних факторов: неправильное питание, вредные привычки (курение, чрезмерное употребление алкоголя), загрязнения окружающей среды, смена климата и прочее?\n\nA) Никак не реагирует.\n\nB) Появляется сухость, раздражение, зуд.\n\nC) Появляется чрезмерный жирный блеск лица и обостряется течение акне.\n\nD) Появляются высыпания в области лба, носа и подбородка.",
                                  reply_markup=kb.response_4_options)
    await state.set_state(SkinTypeTest.question_5)

# Вопрос 6:
@router.callback_query(SkinTypeTest.question_5)
async def handle_question_5(callback: CallbackQuery, state: FSMContext):
    await state.update_data(answer_5=callback.data)
    await callback.message.answer("Вопрос 6: Как ваша кожа реагирует на пребывание на морозе?\n\nA) Появляется румянец или легкое шелушение.\n\nB) Кожа краснеет, появляется сухость и раздражение.\n\nC) Уменьшение жирного блеска.\n\nD) Меньше жирного блеска в Т-зоне; на щеках появляется ощущение стянутости.",
                                  reply_markup=kb.response_4_options)
    await state.set_state(SkinTypeTest.question_6)

# Вопрос 7:
@router.callback_query(SkinTypeTest.question_6)
async def handle_question_6(callback: CallbackQuery, state: FSMContext):
    await state.update_data(answer_6=callback.data)
    await callback.message.answer("Вопрос 7: Как ваша кожа реагирует на жару?\n\nA) Появляется легкий блеск.\n\nB) На коже появляются шелушения, покраснения или зуд.\n\nC) Жирный блеск усиливается на всем лице.\n\nD) Жирный блеск появляется только в Т-зоне.",
                                  reply_markup=kb.response_4_options)
    await state.set_state(SkinTypeTest.question_7)

# Вопрос 8:
@router.callback_query(SkinTypeTest.question_7)
async def handle_question_7(callback: CallbackQuery, state: FSMContext):
    await state.update_data(answer_7=callback.data)
    await callback.message.answer("Вопрос 8: Как часто у вас появляются акне?\n\nA) Никогда. На моей коже нет высыпаний акне.\n\nB) Появляются в период менструации.\n\nC) Появляются после вредной еды.\n\nD) Постоянно, на лице всегда есть акне и воспаления.",
                                  reply_markup=kb.response_4_options)
    await state.set_state(SkinTypeTest.question_8)

# Вопрос 9:
@router.callback_query(SkinTypeTest.question_8)
async def handle_question_8(callback: CallbackQuery, state: FSMContext):
    await state.update_data(answer_8=callback.data)
    await callback.message.answer("Вопрос 9: Есть ли у Вас следы постакне?\n\nA) Да, есть пятна и рубцы (шрамы от прыщей).\n\nB) Нет, на моём лице нет следов постакне.",
                                  reply_markup=kb.response_2_options)
    await state.set_state(SkinTypeTest.question_9)

# Вопрос 10:
@router.callback_query(SkinTypeTest.question_9)
async def handle_question_9(callback: CallbackQuery, state: FSMContext):
    await state.update_data(answer_9=callback.data)
    await callback.message.answer("Вопрос 10: Заметны ли на Вашем лице морщины?\n\nA) Нет, на моём лице нет морщин.\n\nB) Да, на моём лице есть лёгкие поверхностные морщинки.\n\nC) Да, на моём лице есть неглубокие мимические морщины.\n\nD) Да, на моём лице есть глубокие возрастные морщины.",
                                  reply_markup=kb.response_4_options)
    await state.set_state(SkinTypeTest.question_10)

# Вопрос 11:
@router.callback_query(SkinTypeTest.question_10)
async def handle_question_10(callback: CallbackQuery, state: FSMContext):
    await state.update_data(answer_10=callback.data)
    await callback.message.answer("Вопрос 11: Заметны ли на вашем лице покраснения или тонкая сосудистая сеточка на щеках, крыльях носа, скулах?\n\nA) Нет, у меня нет такой проблемы.\n\nB) Да, у меня есть покраснения на лице.",
                                  reply_markup=kb.response_2_options)
    await state.set_state(SkinTypeTest.question_11)

# Вопрос 12:
@router.callback_query(SkinTypeTest.question_11)
async def handle_question_11(callback: CallbackQuery, state: FSMContext):
    await state.update_data(answer_11=callback.data)
    await callback.message.answer("Вопрос 12: Есть ли у вас следы недосыпа или отечностей по утрам?\n\nA) Нет.\n\nB) Да, есть.",
                                  reply_markup=kb.response_2_options)
    await state.set_state(SkinTypeTest.question_12)

# Вопрос 13:
@router.callback_query(SkinTypeTest.question_12)
async def handle_question_12(callback: CallbackQuery, state: FSMContext):
    await state.update_data(answer_12=callback.data)
    await callback.message.answer("Вопрос 13: Вы беременны или планируете беременность?\n\nA) Нет.\n\nB) Да, я беременна в данный момент.\n\nC) Да, я планирую беременность в скором времени.",
                                  reply_markup=kb.response_3_options)
    await state.set_state(SkinTypeTest.question_13)

# Вывод результата теста:
@router.callback_query(SkinTypeTest.question_13)
async def handle_question_3(callback: CallbackQuery, state: FSMContext):
    await state.update_data(answer_13=callback.data)
    await callback.message.answer("Спасибо за ответы! Пожалуйста, подождите, пока я анализирую ваш тип кожи...")
    await state.set_state(SkinTypeTest.calculating_result)
                                  
    # получение данных из состояния
    user_data = await state.get_data()
    skin_type, features, risks = determine_skin_type(user_data)

    # сохранение результата в бд
    await rq.upsert_user(tg_id=callback.from_user.id, 
                         skin_type=skin_type,
                         features=features,
                         risks=risks
                         )

    # Завершение теста
    response_text = (
        f"Тип вашей кожи: {skin_type}\n\n"
        f"Особенности вашей кожи: {', '.join(features)}\n\n"
        f"Риски для вашей кожи: {', '.join(risks) if risks else 'Рисков для вашей кожи нет'}"
    )

    await callback.message.answer(response_text)
    await callback.message.answer(f'Если вдруг Вы сомневаетесь в результатах тестирования, то Вы можете воспользоваться тестом, который легко провести в домашних условиях.\n\nЧтобы самостоятельно определить тип кожи, проведите несложный тест:\n\t1. Начните с очищения кожи. Умойтесь вашим привычным гелем или пенкой и не используйте дополнительно никакие увлажняющие средства.\n\t2. Подождите около 30-40 минут, пока сальные железы не начнут вырабатывать кожный жир\n\t3. Приложите к Т-зоне и щекам папиросную бумагу или салфетки для удаления жирного блеска. Подержите их примерно две минуты.\n\nГотовы оценить результаты?\n\t1. Если все участки кожи оставили обильный жирный след – вероятно, у вас жирный тип кожи.\n\t2. След остался только на бумаге, расположенной в Т-зоне? Ваша кожа, скорей всего, комбинированная.\n\t3. Если вы заметили следы на всех кусочках бумаги, но они не ярко выраженные, то у вас нормальная кожа.\n\t4. Если на салфетке нет никаких следов - кожа сухая.\n\nТочно определить тип кожи при помощи тестирования достаточно сложно. Если Вы хотите получить достоверные данные на счёт особенностей Вашей кожи, рекомендуем обратиться к специалисту.\n\n\nИсточник: https://www.loreal-paris.ru/blog/kak-opredelit-tip-kozhi-lica')

    await state.clear()

# обработка опции "Персональные рекомендации" -> "Получить рекомендации"
@router.callback_query(lambda c: c.data == "get_recommendations")
async def get_recommendations(callback: CallbackQuery):
    await callback.message.answer("Вот персональные рекомендации для ухода за вашим типом кожи, учитывая все её особенности:")
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