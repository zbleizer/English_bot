import asyncio
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from handlers import start
import logging
logging.basicConfig(level=logging.INFO)
from handlers.learn import router as learn_router
from handlers.quiz import router as quiz_router


async def main():
    bot = Bot(
        token='7746881325:AAFiE2vdFxoZUOe-Tuvfs4yysaXQLMW_3Ms',
        default=DefaultBotProperties(parse_mode="HTML")
    )

    dp = Dispatcher()

    dp.include_routers(
        start.router,
        learn_router,
        quiz_router
    )
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())