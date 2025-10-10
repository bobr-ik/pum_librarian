from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import CallbackQuery, Message
import app.keyboards as kb
from aiogram import F
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from database import orm
import models as m
from app import functions as f
from app import patterns as p
from datetime import datetime, timedelta
from math import ceil
import asyncio

rt = Router()


class Form(StatesGroup):
    find_book = State()

class ChooseBook(StatesGroup):
    book_id = State()
    action_with_book = State()


@rt.message(CommandStart())
async def start(message):
    await message.answer('Здравствуйте! Что хотите сделать?', reply_markup=kb.start_keyboard)

@rt.callback_query(F.data == 'start')
async def show_start(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    await callback.message.edit_text("Здравствуйте! Что хотите сделать?", reply_markup=kb.start_keyboard)


@rt.callback_query(F.data == 'find_book')
async def show_find_book(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    await state.set_state(Form.find_book)
    await state.update_data(message_id=callback.message.message_id)
    await callback.message.edit_text("Введите название книги", reply_markup=kb.back_keyboard)


@rt.message(Form.find_book)
async def select_book(message: Message, state: FSMContext):
    books: list[m.BookPosition] = await orm.get_book_position(message.text)
    if not books:
        await message.delete()
        msg = await message.answer(
            text='Книга не найдена или ее уже взяли'
        )
        await asyncio.sleep(3)
        await msg.delete()
        return

    await state.update_data(books=books)
    await message.delete()
    await message.bot.edit_message_text(
        chat_id=message.chat.id, 
        message_id=await state.get_value('message_id'), 
        text="Выберите книгу", 
        parse_mode="HTML",
        reply_markup=kb.books_keyboard(books)
    )


@rt.callback_query(F.data == "back_to_books")
async def select_book(callback: CallbackQuery, state: FSMContext):
    books = await state.get_value('books')
    if not books:
        msg = await callback.message.edit_text(
            text='Книга не найдена или ее уже взяли',
            reply_markup=kb.back_keyboard
        )
        return

    await state.update_data(books=books)
    await callback.message.edit_text(
        text="Выберите книгу", 
        parse_mode="HTML",
        reply_markup=kb.books_keyboard(books)
    )


@rt.callback_query(kb.Book.filter())
async def find_book(callback: CallbackQuery, state: FSMContext, callback_data: kb.Book):    
    books: list[m.BookPosition] = await state.get_value('books')
    
    if (id := await state.get_value('message_id')) != callback.message.message_id:
        await callback.bot.delete_message(chat_id=callback.from_user.id, message_id=id)

    text = ''
    book = f.find_book(callback_data.book_type_id, books)

    await state.update_data(book=book) 

    text += p.book.format(**book.model_dump())

    for locations in book.locations:
        text += p.location.format(**locations.model_dump())

        for positions in locations.positions:
            if positions.shelf and positions.row:
                text += p.local_position.format(**positions.model_dump()) 
            else:
                text += p.no_shelves.format(**positions.model_dump()) 

    await callback.message.edit_text(
        text=text, 
        parse_mode="HTML",
        reply_markup=kb.found_books_keyboard
    )

    await state.update_data(message_id=callback.message.message_id)


@rt.callback_query(F.data == 'select_book')
async def select_location(callback: CallbackQuery, state: FSMContext):
    await callback.answer()

    book: m.BookPosition = await state.get_value('book')

    await callback.message.answer("Выберите локацию", reply_markup=kb.location_keyboard(book))


@rt.callback_query(kb.Location.filter())
async def select_position(callback: CallbackQuery, state: FSMContext, callback_data: kb.Location):
    await callback.answer()

    book: m.BookPosition = await state.get_value('book')
    location = f.find_location(callback_data.location_id, book)
    await state.update_data(location=location)

    await callback.message.edit_text("Выберите место, на котором стоит книга", reply_markup=kb.shelf_keyboard(callback_data.location_id, location))

@rt.callback_query(kb.Position.filter())
async def select_shelf(callback: CallbackQuery, state: FSMContext, callback_data: kb.Position):
    await callback.answer()
    shelf, row = callback_data.shelf, callback_data.row
    book: m.BookPosition = await state.get_value('book')

    if not(shelf and row):
        location: m.Location = f.find_location(callback_data.location_id, book)
    else:
        location: m.Location = await state.get_value('location')
    date = datetime.now() - timedelta(days=15)
    await orm.select_book(book.book_type_id, location.location_id, shelf, row, callback.from_user.id, callback.from_user.username, date)
    await state.clear()

    if shelf and row:
        text = p.chosen_book.format(
            **book.model_dump(), 
            **location.model_dump(), 
            shelf=shelf, 
            row=row, 
            date_start=date, 
            date_return=date + timedelta(days=14)
        )
    else:
        text = p.chosen_book_no_shelves.format(
            **book.model_dump(), 
            **location.model_dump(), 
            date_start=date, 
            date_return=date + timedelta(days=14)
        )
    await callback.message.edit_text(
        text=text, 
        parse_mode="HTML", 
        reply_markup=kb.back_keyboard
    )


@rt.callback_query(kb.AllBooks.filter())
async def show_all_books(callback: CallbackQuery, state: FSMContext, callback_data: kb.AllBooks):
    await callback.answer()
    await state.set_state(ChooseBook.book_id)
    await state.update_data(message_id=callback.message.message_id)

    BOOKS_PER_PAGE = 5

    if not(all_books := await state.get_value('all_books')):
        all_books = await orm.get_all_books()
        await state.update_data(all_books=all_books)
    
    page = callback_data.page

    text = ''
    for elem in all_books[(page - 1) * BOOKS_PER_PAGE:min(page * BOOKS_PER_PAGE, len(all_books))]:
        text += p.book.format(book_type_id=elem[0], book_name=elem[1], author=elem[2])
    await callback.message.edit_text(
        text, 
        parse_mode="HTML", 
        reply_markup=kb.books_pagination_keyboard(page, ceil(len(all_books) / BOOKS_PER_PAGE), page != 1, page != ceil(len(all_books) / BOOKS_PER_PAGE))
    )


@rt.message(ChooseBook.book_id)
async def find_book(message: Message, state: FSMContext):    
    books: list[m.BookPosition] = await orm.get_book_position(message.text)

    if not books:
        await message.delete()
        msg = await message.answer(
            text='Книга не найдена или ее уже взяли. Попробуйте другой id'
        )
        await asyncio.sleep(3)
        await msg.delete()
        return
    
    text = ''
    book = f.find_book_by_id(message.text, books)

    await state.update_data(book=book) 

    text += p.book.format(**book.model_dump())

    for locations in book.locations:
        text += p.location.format(**locations.model_dump())

        for positions in locations.positions:
            if positions.shelf and positions.row:
                text += p.local_position.format(**positions.model_dump()) 
            else:
                text += p.no_shelves.format(**positions.model_dump())

    await message.delete()
    await message.bot.edit_message_text(
        chat_id=message.chat.id, 
        message_id=await state.get_value('message_id'),
        text=text, 
        parse_mode="HTML",
        reply_markup=kb.found_books_keyboard
    )


@rt.callback_query(F.data == 'action_with_book')
async def return_book(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await state.clear()
    data = await orm.get_all_borrowed_books(callback.from_user.id)
    await state.set_state(ChooseBook.action_with_book)
    await state.update_data(books = data)

    text = ''
    for book in data:
        if book.shelf and book.row:
            text += p.book_to_return.format(**book.model_dump())
        else:
            text += p.book_to_return_no_shelves.format(**book.model_dump())
    await callback.message.edit_text(text=text, parse_mode="HTML", reply_markup=kb.return_book_keyboard(data))


@rt.callback_query(kb.ReturnBook.filter())
async def return_book(callback: CallbackQuery, state: FSMContext, callback_data: kb.ReturnBook):
    await callback.answer()
    book = f.find_book_by_local_id(callback_data.book_id, await state.get_value('books'))

    await state.update_data(book_id=book.book_id)

    if book.shelf and book.row:
        await callback.message.edit_text(p.book_to_return.format(**book.model_dump()), reply_markup=kb.book_actions_keyboard, parse_mode="HTML")
    else:
        await callback.message.edit_text(p.book_to_return_no_shelves.format(**book.model_dump()), reply_markup=kb.book_actions_keyboard, parse_mode="HTML")

@rt.callback_query(F.data == 'return_book')
async def return_book(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await orm.return_book(await state.get_value('book_id'), callback.from_user.id)
    await callback.message.edit_text(text='Спасибо, что вернули книгу!', reply_markup=kb.back_keyboard)


@rt.callback_query(F.data == 'extend_book')
async def extend_book(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await orm.extend_book(await state.get_value('book_id'), callback.from_user.id)
    await callback.message.edit_text(text=p.book_extended.format(date_return=datetime.now() + timedelta(days=14)), reply_markup=kb.back_keyboard)