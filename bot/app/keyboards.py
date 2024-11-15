from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)

# Главное меню - ReplyKeyboardMarkup
main_menu = ReplyKeyboardMarkup(keyboard=[                        
    [KeyboardButton(text="Начать анализ")],
    [KeyboardButton(text="Персональные рекомендации")],
    [KeyboardButton(text="История анализов"), KeyboardButton(text="Настройки")]
], resize_keyboard=True)

# Inline меню для опции "Начать анализ"
analysis_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Загрузить фото состава", callback_data="upload_photo")],
    [InlineKeyboardButton(text="Использовать текстовый ввод", callback_data="text_input")]]
)

# Inline меню для опции "Персональные рекомендации"
personal_rec_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Узнать свой тип кожи", callback_data="get_skin_type")],
    [InlineKeyboardButton(text="Получить рекомендации", callback_data="get_recommendations")]]
)

# Inline меню для опции "Настройки"
settings_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Обновить информацию о коже", callback_data="update_skin_info")],
    [InlineKeyboardButton(text="Включить/выключить уведомления", callback_data="toggle_notifications")],
    [InlineKeyboardButton(text="Удалить историю анализов", callback_data="delete_history")]]
)

# Inline меню для "Персональные рекомендации" -> "Узнать свой тип кожи"
response_options = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="A", callback_data="a"),
    InlineKeyboardButton(text="B", callback_data="b"),
    InlineKeyboardButton(text="C", callback_data="c")]])