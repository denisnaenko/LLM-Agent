from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Начать анализ")],
    [KeyboardButton(text="Персональные рекомендации")],
    [KeyboardButton(text="История анализов"), KeyboardButton(text="Настройки")]
])

