from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)

# Главное меню - ReplyKeyboardMarkup
main_menu = ReplyKeyboardMarkup(keyboard=[                        
    [KeyboardButton(text="Начать анализ")],
    [KeyboardButton(text="Персональные рекомендации")],
    [KeyboardButton(text="История анализов"), KeyboardButton(text="Настройки")]
], resize_keyboard=True, input_field_placeholder="Выберите пункт меню:")

# Inline меню для опции "Начать анализ"
analysis_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Загрузить фото упаковки", callback_data="upload_photo")],
    [InlineKeyboardButton(text="Использовать текстовый ввод", callback_data="text_input")],
    [InlineKeyboardButton(text="Назад в меню", callback_data="back_to_main")]]
)

# Inline меню для опции "Персональные рекомендации"
personal_rec_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Ввести данные о коже", callback_data="enter_skin_data")],
    [InlineKeyboardButton(text="Получить рекомендации", callback_data="get_rec")],
    [InlineKeyboardButton(text="Назад в меню", callback_data="back_to_main")]]
)

# Inline меню для опции "Настройки"
settings_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Обновить информацию о коже", callback_data="update_skin_info")],
    [InlineKeyboardButton(text="Включить/выключить уведомления", callback_data="toggle_notifications")],
    [InlineKeyboardButton(text="Удалить историю анализов", callback_data="delete_history")]]
)