from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


admin_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='Добавить книгу', callback_data='admin_add_book'),
            InlineKeyboardButton(text='Удалить книгу', callback_data='admin_delete_book')
        ],
        [
            InlineKeyboardButton(text='Добавить место', callback_data='admin_add_location'),
            InlineKeyboardButton(text='Удалить место', callback_data='admin_delete_location')
        ]
    ]
)