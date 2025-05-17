from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


main_menu = ReplyKeyboardMarkup(

    keyboard=[
        [KeyboardButton(text="📖 Учить слова")],
        [KeyboardButton(text="❓ Квиз")],
        # [KeyboardButton(text="📊 Прогресс")]
    ],
    resize_keyboard=True
)
