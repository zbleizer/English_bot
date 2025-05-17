from aiogram import Router, types
from aiogram.filters import Command
from keyboards import main_menu


router = Router()

@router.message(Command("start"))
async def start(message: types.Message):

    await message.answer(
        "🇬🇧 Добро пожаловать в English Helper!\n"
        "Выберите режим:",
        reply_markup=main_menu
    )

