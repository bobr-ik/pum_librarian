from aiogram import Bot, Dispatcher
from config import settings
import asyncio
from app.handlers import rt
from config import settings
from app.notifications import daily_notification


async def start_bot_async():
    dp = Dispatcher()
    bot = settings.BOT

    dp.include_router(rt)

    asyncio.create_task(daily_notification(bot))
    await dp.start_polling(bot)


def start_bot():

    asyncio.run(start_bot_async())


if __name__ == '__main__':
    start_bot()