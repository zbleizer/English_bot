from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder, ReplyKeyboardMarkup
from database.models import Word
from database.db import get_db
from sqlalchemy import func


router = Router()

main_menu_kb = ReplyKeyboardMarkup(

    keyboard=[
        [types.KeyboardButton(text="📖 Учить слова")],
        [types.KeyboardButton(text="❓ Квиз")],
        [types.KeyboardButton(text="📊 Прогресс")]
    ],
    resize_keyboard=True
)

current_words = {}


async def get_random_word():

    db = next(get_db())
    word = db.query(Word).filter_by(is_learned=False).order_by(func.random()).first()
    db.close()
    return word


@router.message(Command("learn"))
@router.message(F.text == "📖 Учить слова")
async def start_learning(message: types.Message):

    word = await get_random_word()

    if not word:
        await message.answer("🎉 Вы выучили все слова!", reply_markup=main_menu_kb)
        return

    current_words[message.from_user.id] = word

    kb = ReplyKeyboardBuilder()
    kb.button(text="Показать перевод")
    kb.button(text="Знаю это слово")
    kb.button(text="↩️ Назад")
    kb.adjust(2)

    await message.answer(
        f"🇬🇧 Слово: <b>{word.english}</b>\n",
        parse_mode="HTML",
        reply_markup=kb.as_markup(resize_keyboard=True)
    )


@router.message(F.text == "Показать перевод")
async def show_translation(message: types.Message):

    word = current_words.get(message.from_user.id)
    if word:
        await message.answer(f"🇷🇺 Перевод: <b>{word.russian}</b>", parse_mode="HTML")


@router.message(F.text == "Знаю это слово")
async def mark_as_learned(message: types.Message):

    word = current_words.get(message.from_user.id)
    if not word:
        return

    db = next(get_db())
    try:
        db_word = db.query(Word).filter_by(id=word.id).first()
        if db_word:
            db_word.is_learned = True
            db.commit()
            await message.answer("✅ Отлично! Слово изучено.")
    finally:
        db.close()

    await start_learning(message)


@router.message(F.text == "↩️ Назад")
async def back_to_menu_handler(message: types.Message):

    if message.from_user.id in current_words:
        del current_words[message.from_user.id]

    await message.answer(
        "Выберите действие:",
        reply_markup=main_menu_kb
    )