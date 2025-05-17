from aiogram import Router, types, F, Bot
from aiogram.filters import Command
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from database.models import Word
from database.db import get_db
from keyboards import main_menu
from sqlalchemy import func

router = Router()

waiting_for_answer = {}
user_scores = {}


async def get_random_word(user_id: int):
    db = next(get_db())
    return db.query(Word).filter_by(is_learned=False).order_by(func.random()).first()


async def get_progress_stats(user_id: int):
    db = next(get_db())
    try:
        total_words = db.query(Word).count()
        learned_words = db.query(Word).filter_by(is_learned=True).count()
        return total_words, learned_words
    finally:
        db.close()


@router.message(Command("quiz"))
@router.message(F.text == "❓ Квиз")
async def start_learning(message: types.Message, bot: Bot):
    word = await get_random_word(message.from_user.id)

    if not word:
        await message.answer("🎉 Вы изучили все слова!", reply_markup=main_menu)
        return

    waiting_for_answer[message.from_user.id] = word

    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(text="Показать перевод"))
    builder.row(types.KeyboardButton(text="Следующее слово"))
    builder.row(types.KeyboardButton(text="Подсказка"))
    builder.row(types.KeyboardButton(text="📊 Прогресс"))
    builder.row(types.KeyboardButton(text="↩️ Назад в меню"))

    await message.answer(
        f"Как перевести слово: <b>{word.english}</b>?\n\n"
        "Напишите перевод или выберите действие:",
        parse_mode="HTML",
        reply_markup=builder.as_markup(resize_keyboard=True)
    )


@router.message(F.text == "📊 Прогресс")
async def show_progress(message: types.Message):
    total, learned = await get_progress_stats(message.from_user.id)
    progress_percent = (learned / total * 100) if total > 0 else 0

    progress_bar = "🟩" * int(progress_percent / 10) + "⬜️" * (10 - int(progress_percent / 10))

    await message.answer(
        f"📊 Ваш прогресс:\n\n"
        f"{progress_bar} {progress_percent:.1f}%\n\n"
        f"✅ Изучено: {learned} слов\n"
        f"📚 Всего: {total} слов\n\n"
        f"🏆 Текущий счет: {user_scores.get(message.from_user.id, 0)}",
        parse_mode="HTML"
    )


@router.message(F.text == "Показать перевод")
async def show_translation(message: types.Message):
    if message.from_user.id not in waiting_for_answer:
        return
    word = waiting_for_answer[message.from_user.id]
    await message.answer(f"🇷🇺 Перевод: <b>{word.russian}</b>", parse_mode="HTML")


@router.message(F.text == "Следующее слово")
async def next_word(message: types.Message, bot: Bot):
    await start_learning(message, bot)


@router.message(F.text == "Подсказка")
async def give_hint(message: types.Message):
    if message.from_user.id not in waiting_for_answer:
        return

    word = waiting_for_answer[message.from_user.id]
    hint = word.russian[:3] + "..."
    await message.answer(f"Подсказка: начинается на <b>{hint}</b>", parse_mode="HTML")


@router.message(F.text.casefold() == "назад в меню")
async def back_to_menu(message: types.Message):
    if message.from_user.id in waiting_for_answer:
        del waiting_for_answer[message.from_user.id]

    if message.from_user.id in user_scores:
        del user_scores[message.from_user.id]

    await message.answer(
        "Возвращаемся в главное меню...",
        reply_markup=types.ReplyKeyboardRemove()
    )
    await message.answer(
        "Выберите действие:",
        reply_markup=main_menu
    )


@router.message(F.text)
async def check_answer(message: types.Message, bot: Bot):
    if message.from_user.id not in waiting_for_answer:
        return

    word = waiting_for_answer[message.from_user.id]
    user_answer = message.text.strip().lower()

    if user_answer == "↩️ назад в меню":
        await back_to_menu(message)
        return
    if user_answer == "📊 прогресс":
        await show_progress(message)
        return

    if user_answer == word.russian.lower():
        db = next(get_db())
        try:
            word.is_learned = True
            db.commit()
        finally:
            db.close()

        user_scores[message.from_user.id] = user_scores.get(message.from_user.id, 0) + 1
        await message.answer(
            f"✅ Верно! Ваш счет: {user_scores[message.from_user.id]}",
            reply_markup=types.ReplyKeyboardRemove()
        )
    else:
        await message.answer(
            f"❌ Неправильно. Правильный ответ: <b>{word.russian}</b>",
            parse_mode="HTML"
        )

    builder = ReplyKeyboardBuilder()
    builder.row(types.KeyboardButton(text="Следующее слово"))
    builder.row(types.KeyboardButton(text="📊 Прогресс"))
    builder.row(types.KeyboardButton(text="↩️ Назад в меню"))
    await message.answer(
        "Продолжим?",
        reply_markup=builder.as_markup(resize_keyboard=True)
    )