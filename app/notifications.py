from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio
from datetime import datetime, timedelta
from database import orm
from app import patterns as p

async def daily_notification(bot: Bot):
    while True:
        # Ждем до 9:00 следующего дня
        now = datetime.now()
        target_time = now.replace(hour=9, minute=0, second=0, microsecond=0)
        
        if now > target_time:
            target_time += timedelta(days=1)
        
        wait_seconds = (target_time - now).total_seconds()
        await asyncio.sleep(wait_seconds)
        
        # Отправляем сообщения
        users = await orm.get_notifications_data()
        for user in users:
            try:
                if user.shelf and user.row:
                    text = p.notification.format(**user.model_dump())
                else:
                    text = p.notification_no_shelves.format(**user.model_dump())
                await bot.send_message(
                    user.tg_id,
                    text=text,
                    parse_mode="HTML"
                )
                    
            except Exception as e:
                print(f"Ошибка отправки пользователю {user.tg_id}: {e}")