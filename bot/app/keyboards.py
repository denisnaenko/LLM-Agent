from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)

# Главное меню - ReplyKeyboardMarkup
main_menu = ReplyKeyboardMarkup(keyboard=[                        
    [KeyboardButton(text="Начать анализ")],
    [KeyboardButton(text="Персональные рекомендации")],
    [KeyboardButton(text="История анализов")],
    [KeyboardButton(text="Настройки")]
], resize_keyboard=True, input_field_placeholder="Выберите пункт меню:")

# Inline меню для опции "Начать анализ"
analysis_menu = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Загрузить фото упаковки", callback_data="upload_photo")],
    [InlineKeyboardButton(text="Использовать текстовый ввод", callback_data="text_input")],
    [InlineKeyboardButton(text="Назад в меню", callback_data="back_to_main")]]
)