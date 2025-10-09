from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
import models as m
from app import functions as f
from typing import Optional


class Book(CallbackData, prefix='book'):
    book_type_id: int

class Location(CallbackData, prefix='location'):
    location_id: int

class Position(CallbackData, prefix='position'):
    shelf: Optional[int]
    row: Optional[int]
    location_id: Optional[int] = None

class AllBooks(CallbackData, prefix='all_books'):
    page: int = 1

class ReturnBook(CallbackData, prefix='return_book'):
    book_id: int


start_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='Все книги', callback_data=AllBooks().pack()),
            InlineKeyboardButton(text='Вернуть/продлить', callback_data='action_with_book')
        ],
        [
            InlineKeyboardButton(text='Узнать где книга', callback_data='find_book')
        ]
    ]
)

back_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='В начало', callback_data='start')
        ]
    ]
)

found_books_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='Взять книгу', callback_data='select_book')
        ],
        [
            InlineKeyboardButton(text='Назад', callback_data='back_to_books')
        ]
    ]
)

book_actions_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='Вернуть', callback_data='return_book'),
            InlineKeyboardButton(text='Продлить', callback_data='extend_book')
        ],
        [
            InlineKeyboardButton(text='Назад', callback_data='start')
        ]
    ]
)


def books_keyboard(books: list[m.BookPosition]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for book in books:
        kb.add(
            InlineKeyboardButton(text=book.book_name, callback_data=Book(book_type_id=book.book_type_id).pack())
        )
    kb.add(
        InlineKeyboardButton(text='Назад', callback_data='find_book')
    )
    return kb.adjust(2).as_markup()


def location_keyboard(book: m.BookPosition) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for location in book.locations:
        if all(map(lambda x: x.shelf and x.row, location.positions)):
            kb.add(
                InlineKeyboardButton(text=location.location_name, callback_data=Location(location_id=location.location_id).pack())
            )
        else:
            kb.add(
                InlineKeyboardButton(text=location.location_name, callback_data=Position(shelf=None, row=None, location_id=location.location_id).pack(), disabled=True)
            )
    kb.add(
        InlineKeyboardButton(text='Назад', callback_data=Book(book_type_id=book.book_type_id).pack())
    )
    return kb.adjust(2).as_markup()


def shelf_keyboard(location_id, location: m.Location) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for position in location.positions:
        kb.add(
            InlineKeyboardButton(text=f'{position.shelf} стелаж, {position.row} полка', callback_data=Position(shelf=position.shelf, row=position.row).pack())
        )
    kb.add(
        InlineKeyboardButton(text='Назад', callback_data=Location(location_id=location_id).pack())
    )
    return kb.adjust(2).as_markup()


def books_pagination_keyboard(page: int, total_len: int, is_left: bool = True, is_right: bool = True) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    if is_left:
        kb.add(InlineKeyboardButton(text='<', callback_data=AllBooks(page=page - 1).pack()))
    else:
        kb.add(InlineKeyboardButton(text=' ', callback_data=AllBooks(page=page).pack()))

    kb.add(InlineKeyboardButton(text=f'Страница {page}/{total_len}', callback_data=AllBooks(page=page).pack()))

    if is_right:
        kb.add(InlineKeyboardButton(text='>', callback_data=AllBooks(page=page + 1).pack()))
    else:
        kb.add(InlineKeyboardButton(text=' ', callback_data=AllBooks(page=page).pack()))
    
    kb.add(InlineKeyboardButton(text='Назад', callback_data='start'))

    return kb.adjust(3).as_markup()


def return_book_keyboard(books):
    kb = InlineKeyboardBuilder()
    for book in books:
        kb.add(InlineKeyboardButton(text=book.book_name, callback_data=ReturnBook(book_id=book.book_id).pack()))
    kb.add(InlineKeyboardButton(text='Назад', callback_data='start'))
    return kb.adjust(2).as_markup()