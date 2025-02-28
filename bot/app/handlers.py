import app.keyboards as kb
import app.database.requests as rq
import os

from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery, FSInputFile
from .helpers.skin_test import determine_skin_type
from .services.cropper import crop_object_async
from .services.find_func import analyze_ingredients
from .services.personal_rec_request import get_result_message
from .services.llama_request import query_llm
from .helpers.get_user_skin_data import get_user_data
from .helpers.ingredient_invalidation import is_valid_ingredients_text
from .helpers.create_pdf import create_pdf
import types

router = Router()

# Состояние ожидания загрузки фото для анализа
class UploadPhotoState(StatesGroup):
    waiting_for_photo = State()

# Состояние ожидания ввода текста пользователем для анализа
class TextInputState(StatesGroup):
    waiting_for_text = State()

# Состояния для вопросов теста на тип кожи
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


# Логика получения рекомендаций
async def process_recommendations(callback_or_message, state: FSMContext, tg_id):
    # Очистка состояния
    await state.clear()

    # Получение данных пользователя
    skin_type, features, risks = get_user_data(tg_id)

    if not skin_type:
        # Если пользователя нет в БД
        response = (
            "Пожалуйста, пройдите тест на определение типа кожи перед тем, как получать персональные рекомендации."
        )
        if isinstance(callback_or_message, CallbackQuery):
            await callback_or_message.message.answer(response)
        else:
            await callback_or_message.answer(response)
        return

    # Запрос к модели
    loading_message = (
        "Учёл все особенности вашей кожи!\n\n"
        "Уже готовлю для вас рекомендации! Это займёт не более 20 секунд :)"
    )
    if isinstance(callback_or_message, CallbackQuery):
        await callback_or_message.message.answer(loading_message)
    else:
        await callback_or_message.answer(loading_message)

    # Получение рекомендаций
    recommendations = await get_result_message(skin_type, features, risks)

    if recommendations == "error3":
        response = "Произошла ошибка при получении рекомендаций. Пожалуйста, попробуйте ещё раз!"
    else:
        response = (
            f"Вот персональные рекомендации средств ухода за вашим типом кожи:\n\n{recommendations}"
        )

    # Отправка ответа
    if isinstance(callback_or_message, CallbackQuery):
        await callback_or_message.message.answer(response)
    else:
        await callback_or_message.answer(response)


@router.message()
async def handle_global_navigation(message: Message, state: FSMContext):
    """
    Глобавльный обработчки для переключения между функциями, независимо от текущего состояния.
    """
    current_state = await state.get_state()
    user_input = message.text

    # Обработка загруженного фото
    if message.photo: 
        await state.set_state(UploadPhotoState.waiting_for_photo)
        await handle_photo(message, state)
        return

    # Обработка кнопочных команд
    if await handle_other_commands(message, state): 
        return
    
    # Обработка состава по тексту
    if current_state == TextInputState.waiting_for_text:
        await handle_text_input(message, state)
        return

    # Запрос к LLM для определения действия
    prompt = f"""
    Пользователь ввел следующий запрос: "{user_input}".  

    Верни только одно слово из списка: upload_photo, text_input, get_skin_type, get_recommendations
    
    Твоя задача: определить, какое из указанных действий наиболее подходит запросу пользователя. Выбери только одно действие из списка:  
    1. upload_photo — Анализировать состав по фото.  
    2. text_input — Анализировать состав на основе текста.  
    3. get_skin_type — Определить тип или состояние кожи.  
    4. get_recommendations — Предложить рекомендации по уходу за кожей.  

    Ограничения:  
    1. Анализируй только текст на русском языке. Если текст содержит слова на других языках, возвращай "None".  
    2. Если запрос слишком короткий (менее 3 слов) или не содержит конкретного смысла, возвращай "None". Примеры таких запросов: "аыаыаы", "что делать?", "привет".  
    3. Если текст явно бессмысленный или случайный набор символов, букв, цифр или слов, возвращай "None".  
    4. Если запрос содержит слова, связанные с фото или изображениями (например, "фото", "картинка", "загрузить фото"), выбери "upload_photo".  
    5. Если запрос содержит слова, связанные с текстовым анализом состава (например, "анализ текста", "ингредиенты", "состав"), выбери "text_input".  
    6. Если запрос содержит слова, связанные с кожей (например, "тип кожи", "состояние кожи", "тест"), выбери "get_skin_type".  
    7. Если пользователь просит рекомендации (например, "подскажи, что мне подойдет", "какие средства выбрать", "совет"), выбери "get_recommendations".  

    Важно:  
    - Не пытайся угадать, если запрос не подходит ни под одно действие. В таких случаях верни "None".  
    - Твой ответ должен быть только одним из следующих: upload_photo, text_input, get_skin_type, get_recommendations или None.  

    Примеры запросов и действий:  
    1. Запрос: "Хочу загрузить фото для анализа." → Ответ: upload_photo  
    2. Запрос: "Проанализируй состав крема: вода, глицерин, масло." → Ответ: text_input  
    3. Запрос: "Анализ по тексту" → Ответ: text_input
    4. Запрос: "Какой у меня тип кожи?" → Ответ: get_skin_type  
    5. Запрос: "Посоветуй что-нибудь для сухой кожи." → Ответ: get_recommendations  
    6. Запрос: "ааа фвафва ываывавы" → Ответ: None
    7. Запрос: "INGREDIENTS: Glycerin, Aqua (Hungarian Thermal Water), Silt (Hungarian Mud), Copper Gluconate, Cetearyl Olivate, Lava Powder, Sorbitan Olivate" → Ответ: None
    """
    action = await query_llm(prompt)
    action.strip()

    if "upload_photo" in action:
        await state.clear()
        await message.answer("Загрузите фото состава для анализа:")
        await state.set_state(UploadPhotoState.waiting_for_photo)

    elif "text_input" in action:
        await state.set_state(TextInputState.waiting_for_text)
        await message.answer("Введите состав вашего средства для анализа:")

    elif "get_skin_type" in action:
        await message.answer("Пройдите тест, чтобы определить ваш тип кожи и её особенности:")
        await message.answer("Вопрос 1: Какие ощущения испытывает ваша кожа после умывания?\n\nA) Дискомфорт отсутствует, кожа свежая, сияющая.\n\nB) Появляется чувство стянутости, сухость, дискомфорт.\n\nC) Уже через 20 минут после умывания появляется незначительный жирный блеск лица.\n\nD) После умывания появляется чрезмерный блеск лица в Т-зоне, область щек остается матовой.",
                                  reply_markup=kb.response_4_options)
        await state.set_state(SkinTypeTest.question_1)    

    elif "get_recommendations" in action:
        await process_recommendations(message, state, message.from_user.id)

    else:
        await message.answer(f"Не удалось распознать действие. Попробуйте ещё раз.")
        return
    
    return True


# Обработка команды /start
@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(f"👋🏻 Добро пожаловать в “Агент Косметик”!\n\n"
                         f"Я Ваш помощник в подборе качественного и подходящего именно Вам косметического ухода! Я помогу Вам выбрать лучшие косметические средства, основываясь на их составе, а также составлю рекомендации по уходу за кожей специально для Вас.\n\n\n"
                         f"📋 Что я могу для Вас сделать?\n\n"
                         f"• Проанализировать состав Вашего косметического средства по фото или тексту и дать подробный отчёт об используемых в нём опасных ингредиентов .\n\n"
                         f"• Определить ваш тип кожи и выявить её особенности при помощи тестирования.\n\n"
                         f"• Подобрать для вас персональный уход за кожей.\n\n\n"
                         f"👉🏻 Чтобы ознакомиться с пользовательским соглашением воспользуйтесь командой /help\n\n\n"
                         f"Приступим! Отправьте мне сообщение с действием, которое хотите выполнить, либо воспользуйтесь навигацией по кнопкам.",
                         
                         reply_markup=kb.main_menu)


# Обработка команды /help
async def cmd_help(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(f"• Пользовательское соглашение:\n https://denisnaenko.github.io/LLM-Agent/user-agreement.html\n\n"
                         f"• Обратная связь: @grinnbi")

# Обработка опции "Начать анализ"
@router.message(lambda message: message.text == "Начать анализ")
async def start_analysis(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Выберите действие для анализа состава:", reply_markup=kb.analysis_menu)


# Обработка опции "Начать анализ" -> "Загрузить фото состава"
@router.callback_query(lambda c: c.data == "upload_photo")
async def upload_photo(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Загрузите фото состава для анализа")
    await state.set_state(UploadPhotoState.waiting_for_photo)
    await callback.answer()

# [SUB] Обработка загруженного фото в состоянии 'waiting_for_photo'
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
        result, total_msg = await analyze_ingredients()

        document_path = "pdf/Ингредиенты.pdf"
        await create_pdf(total_msg, document_path)
    
        pdf_file = FSInputFile(document_path)
        await message.answer(result)
        await message.answer_document(pdf_file)

    os.remove(destination)  # удаляем временный файл
    await state.clear()
    

# Обработка опции "Начать анализ" -> "Использовать текстовый ввод"
@router.callback_query(lambda c: c.data == "text_input")
async def text_input(callback: CallbackQuery, state: FSMContext):    
    await state.clear()
    await state.set_state(TextInputState.waiting_for_text)
    
    await callback.message.answer("Введите состав вашего средства для анализа:")
    await callback.answer()

# [SUB] Получение введённого текста и анализ
@router.message(TextInputState.waiting_for_text)
async def handle_text_input(message: Message, state: FSMContext):
    
    user_text = message.text
    if await handle_other_commands(message, state): return

    # Проверка корректности введённого состава
    is_valid, validation_message = await is_valid_ingredients_text(user_text)

    if not is_valid:
        # Отправка сообщения о проблеме
        await message.answer(validation_message)
        
        await state.clear()
        await state.set_state(TextInputState.waiting_for_text)
        return
    
    # Передача текста в функцию анализа
    result, total_msg = await analyze_ingredients(user_text)

    document_path = "pdf/Ингредиенты.pdf"
    await create_pdf(total_msg, document_path)
    
    # Отправка результата
    pdf_file = FSInputFile(document_path)
    await message.answer(result)
    await message.answer_document(pdf_file)

    await state.clear()


# Обработка опции "Персональные рекомендации"
@router.message(lambda message: message.text == "Персональные рекомендации")
async def personal_rec(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Выберите действие для персональных рекомендаций:", reply_markup=kb.personal_rec_menu)


# Обработка опции "Персональные рекомендации" -> "Узнать свой тип кожи"
# [SUB] Вопрос 1:
@router.callback_query(lambda c: c.data == "get_skin_type")
async def get_skin_type(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await callback.message.answer("Пройдите тест, чтобы определить ваш тип кожи и её особенности:")
    await callback.message.answer("Вопрос 1: Какие ощущения испытывает ваша кожа после умывания?\n\nA) Дискомфорт отсутствует, кожа свежая, сияющая.\n\nB) Появляется чувство стянутости, сухость, дискомфорт.\n\nC) Уже через 20 минут после умывания появляется незначительный жирный блеск лица.\n\nD) После умывания появляется чрезмерный блеск лица в Т-зоне, область щек остается матовой.",
                                  reply_markup=kb.response_4_options)
    await state.set_state(SkinTypeTest.question_1)    

# [SUB] Вопрос 2:
@router.callback_query(SkinTypeTest.question_1)
async def handle_question_1(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.update_data(answer_1=callback.data)
    await callback.message.answer("Вопрос 2: Какие ощущения испытывает кожа, если пренебречь этапом её увлажнения?\n\nA) Не использую увлажняющий крем, без него кожа чувствует себя отлично.\n\nB) Увлажняющий крем - незаменимый этап моей бьюти-рутины, так как без него кожа сухая и стянутая.\n\nС) Без увлажнения жирный блеск лица усиливается.\n\nD) Без увлажнения жирный блеск лица усиливается в Т-зоне, область щек остается матовой.",
                                  reply_markup=kb.response_4_options)
    await state.set_state(SkinTypeTest.question_2)

# [SUB] Вопрос 3:
@router.callback_query(SkinTypeTest.question_2)
async def handle_question_2(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.update_data(answer_2=callback.data)
    await callback.message.answer("Вопрос 3: Свойственен ли для вашей кожи жирный блеск?\n\nA) Нет, жирный блеск отсутствует.\n\nB) Лёгкий жирный блеск появляется к концу дня.\n\nC) Да, присутствует на всем лице.\n\nD) Иногда жирный блеск появляется в Т-зоне.",
                                  reply_markup=kb.response_4_options)
    await state.set_state(SkinTypeTest.question_3)

# [SUB] Вопрос 4:
@router.callback_query(SkinTypeTest.question_3)
async def handle_question_3(callback: CallbackQuery, state: FSMContext):
    await state.update_data(answer_3=callback.data)
    await callback.message.answer("Вопрос 4: Оцените состояние пор на вашем лице\n\nA) Поры незаметны, высыпания практически не появляются.\n\nB) Поры практически незаметны, высыпания появляются редко.\n\nC) Поры преимущественно расширенные, на лице имеются несовершенства: прыщи, черные точки, сыпь.\n\nD) Поры расширены только в области лба, носа и подбородка. В U-зоне пор нет или они слабозаметны.",
                                  reply_markup=kb.response_4_options)
    await state.set_state(SkinTypeTest.question_4)

# [SUB] Вопрос 5:
@router.callback_query(SkinTypeTest.question_4)
async def handle_question_4(callback: CallbackQuery, state: FSMContext):
    await state.update_data(answer_4=callback.data)
    await callback.message.answer("Вопрос 5: Реагирует ли ваша кожа на влияние внешних и внутренних факторов: неправильное питание, вредные привычки (курение, чрезмерное употребление алкоголя), загрязнения окружающей среды, смена климата и прочее?\n\nA) Никак не реагирует.\n\nB) Появляется сухость, раздражение, зуд.\n\nC) Появляется чрезмерный жирный блеск лица и обостряется течение акне.\n\nD) Появляются высыпания в области лба, носа и подбородка.",
                                  reply_markup=kb.response_4_options)
    await state.set_state(SkinTypeTest.question_5)

# [SUB] Вопрос 6:
@router.callback_query(SkinTypeTest.question_5)
async def handle_question_5(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.update_data(answer_5=callback.data)
    await callback.message.answer("Вопрос 6: Как ваша кожа реагирует на пребывание на морозе?\n\nA) Появляется румянец или легкое шелушение.\n\nB) Кожа краснеет, появляется сухость и раздражение.\n\nC) Уменьшение жирного блеска.\n\nD) Меньше жирного блеска в Т-зоне; на щеках появляется ощущение стянутости.",
                                  reply_markup=kb.response_4_options)
    await state.set_state(SkinTypeTest.question_6)

# [SUB] Вопрос 7:
@router.callback_query(SkinTypeTest.question_6)
async def handle_question_6(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.update_data(answer_6=callback.data)
    await callback.message.answer("Вопрос 7: Как ваша кожа реагирует на жару?\n\nA) Появляется легкий блеск.\n\nB) На коже появляются шелушения, покраснения или зуд.\n\nC) Жирный блеск усиливается на всем лице.\n\nD) Жирный блеск появляется только в Т-зоне.",
                                  reply_markup=kb.response_4_options)
    await state.set_state(SkinTypeTest.question_7)

# [SUB] Вопрос 8:
@router.callback_query(SkinTypeTest.question_7)
async def handle_question_7(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.update_data(answer_7=callback.data)
    await callback.message.answer("Вопрос 8: Как часто у вас появляются акне?\n\nA) Никогда. На моей коже нет высыпаний акне.\n\nB) Появляются в период менструации.\n\nC) Появляются после вредной еды.\n\nD) Постоянно, на лице всегда есть акне и воспаления.",
                                  reply_markup=kb.response_4_options)
    await state.set_state(SkinTypeTest.question_8)

# [SUB] Вопрос 9:
@router.callback_query(SkinTypeTest.question_8)
async def handle_question_8(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.update_data(answer_8=callback.data)
    await callback.message.answer("Вопрос 9: Есть ли у Вас следы постакне?\n\nA) Да, есть пятна и рубцы (шрамы от прыщей).\n\nB) Нет, на моём лице нет следов постакне.",
                                  reply_markup=kb.response_2_options)
    await state.set_state(SkinTypeTest.question_9)

# [SUB] Вопрос 10:
@router.callback_query(SkinTypeTest.question_9)
async def handle_question_9(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.update_data(answer_9=callback.data)
    await callback.message.answer("Вопрос 10: Заметны ли на Вашем лице морщины?\n\nA) Нет, на моём лице нет морщин.\n\nB) Да, на моём лице есть лёгкие поверхностные морщинки.\n\nC) Да, на моём лице есть неглубокие мимические морщины.\n\nD) Да, на моём лице есть глубокие возрастные морщины.",
                                  reply_markup=kb.response_4_options)
    await state.set_state(SkinTypeTest.question_10)

# [SUB] Вопрос 11:
@router.callback_query(SkinTypeTest.question_10)
async def handle_question_10(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.update_data(answer_10=callback.data)
    await callback.message.answer("Вопрос 11: Заметны ли на вашем лице покраснения или тонкая сосудистая сеточка на щеках, крыльях носа, скулах?\n\nA) Нет, у меня нет такой проблемы.\n\nB) Да, у меня есть покраснения на лице.",
                                  reply_markup=kb.response_2_options)
    await state.set_state(SkinTypeTest.question_11)

# [SUB] Вопрос 12:
@router.callback_query(SkinTypeTest.question_11)
async def handle_question_11(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.update_data(answer_11=callback.data)
    await callback.message.answer("Вопрос 12: Есть ли у вас следы недосыпа или отечностей по утрам?\n\nA) Нет.\n\nB) Да, есть.",
                                  reply_markup=kb.response_2_options)
    await state.set_state(SkinTypeTest.question_12)

# [SUB] Вопрос 13:
@router.callback_query(SkinTypeTest.question_12)
async def handle_question_12(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.update_data(answer_12=callback.data)
    await callback.message.answer("Вопрос 13: Вы беременны или планируете беременность?\n\nA) Нет.\n\nB) Да, я беременна в данный момент.\n\nC) Да, я планирую беременность в скором времени.",
                                  reply_markup=kb.response_3_options)
    await state.set_state(SkinTypeTest.question_13)

# [SUB] Вывод результата теста:
@router.callback_query(SkinTypeTest.question_13)
async def handle_question_13(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.update_data(answer_13=callback.data)
    await state.set_state(SkinTypeTest.calculating_result)

    # Получение данных из состояния
    user_data = await state.get_data()
    skin_type, features, risks = await determine_skin_type(user_data)

    # Сохранение результата в бд
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

    await callback.message.answer(f"Cпасибо за ответы! Вот результаты теста:\n\n"
                                  f"{response_text}\n\n"
                                  f"Если вдруг вы сомневаетесь в результатах тестирования, то вы можете воспользоваться тестом, который легко провести в домашних условиях.",
                                  reply_markup=kb.response_skin_test)
    
    await state.clear()


# Обработка опции "Персональные рекомендации" -> "Узнать свой тип кожи" -> "Самостоятельно определить тип кожи"
@router.callback_query(lambda c: c.data == "show_skin_test")
async def show_skin_test(callback: CallbackQuery):
    await callback.answer()
    await callback.message.answer(f'Чтобы самостоятельно определить тип кожи, проведите несложный тест:\n\t1. Начните с очищения кожи. Умойтесь вашим привычным гелем или пенкой и не используйте дополнительно никакие увлажняющие средства.\n\t2. Подождите около 30-40 минут, пока сальные железы не начнут вырабатывать кожный жир\n\t3. Приложите к Т-зоне и щекам папиросную бумагу или салфетки для удаления жирного блеска. Подержите их примерно две минуты.\n\nГотовы оценить результаты?\n\t1. Если все участки кожи оставили обильный жирный след – вероятно, у вас жирный тип кожи.\n\t2. След остался только на бумаге, расположенной в Т-зоне? Ваша кожа, скорей всего, комбинированная.\n\t3. Если вы заметили следы на всех кусочках бумаги, но они не ярко выраженные, то у вас нормальная кожа.\n\t4. Если на салфетке нет никаких следов - кожа сухая.\n\nТочно определить тип кожи при помощи тестирования достаточно сложно. Если Вы хотите получить достоверные данные на счёт особенностей Вашей кожи, рекомендуем обратиться к специалисту.\n\n\nИсточник: https://www.loreal-paris.ru/blog/kak-opredelit-tip-kozhi-lica')


# Обработка опции "Персональные рекомендации" -> "Получить рекомендации"
@router.callback_query(lambda c: c.data == "get_recommendations")
async def get_recommendations(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await process_recommendations(callback, state, callback.from_user.id)


# [HELP] Обработка перехода между опциями
@router.message(F.text)
async def handle_other_commands(message: Message, state: FSMContext):
    await state.clear()
    if message.text == "/start":
        await cmd_start(message, state)
    elif message.text == "Персональные рекомендации":
        await personal_rec(message, state)
    elif message.text == "Начать анализ":
        await start_analysis(message, state)
    elif message.text == "/help":
        await cmd_help(message, state)
    else:
        return False
    
    return True


# Обработка команды /help
@router.message(Command('help')) 
async def get_help(message: Message):
    await message.answer("Это команда /help")