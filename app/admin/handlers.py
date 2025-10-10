from aiogram import Router
from aiogram.types import CallbackQuery, Message
import app.admin.keyboards as kb
from aiogram import F
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from database import orm
import models as m
from app import functions as f
from app.admin import patterns as p
from datetime import datetime, timedelta
from config import settings
rt = Router()


class Book(StatesGroup):
    book_type_id = State()


@rt.message(lambda message: message.from_user.id in settings.ADMIN_ID and message.text == '/admin')
async def admin_start(message):
    await message.answer('Здравствуйте, мистер админ. Это ваша модераторская рубка', reply_markup=kb.admin_keyboard)


@rt.callback_query(F.data == 'admin_add_book')
async def admin_find_book(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    ...