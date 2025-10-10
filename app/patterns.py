book = '''
<b>==📖<u>{book_name}</u>📖==</b>
📖 автор: {author}
📁 id: {book_type_id}'''

location = '''

<b>--{location_name}--</b>
<i>{description}</i>
'''

local_position = '''
 • {shelf} стелаж, {row} полка  <b>(x{amount})</b>'''

chosen_book = """
{date_start:%d.%m.%Y}
Вы взяли книгу <b>{book_name}</b>

📖 автор: {author}
📁 id: {book_type_id}

<b>--{location_name}--</b>
<i>{description}</i>

 • {shelf} стелаж, {row} полка

Не забудьте вернуть ее или продлить срок аренды до <b>{date_return:%d.%m.%Y}</b> (2 недели)
"""

chosen_book_no_shelves = """
{date_start:%d.%m.%Y}
Вы взяли книгу <b>{book_name}</b>

📖 автор: {author}
📁 id: {book_type_id}

<b>--{location_name}--</b>
<i>{description}</i>

Не забудьте вернуть ее или продлить срок аренды до <b>{date_return:%d.%m.%Y}</b> (2 недели)
"""

all_books = '''
<b>ВЫБЕРИТЕ КНИГУ И НАПИШИТЕ ЕЕ id БОТУ</b>
'''

no_shelves = '''
 • Все в одном месте <b>(x{amount})</b>'''


to_return_start = '''
Книги, которые вам нужно вернуть:
'''

book_to_return = '''
<b>==📖<u>{book_name}</u>📖==</b>
📖 автор: {author}
📁 id: {book_type_id}
Вернуть до: <b>{date_return:%d.%m.%Y}</b>
Куда: <b>{location_name} стелаж {shelf}, полка {row}</b>
'''

book_to_return_no_shelves = '''
<b>==📖<u>{book_name}</u>📖==</b>
📖 автор: {author}
📁 id: {book_type_id}
Вернуть до: <b>{date_return:%d.%m.%Y}</b>
Куда: <b>{location_name}</b>
'''

to_return_end = '''
Выберите книгу, которую хотите вернуть или продлить'''


notification = '''
ВНИМАНИЕ! Вы не вернули книгу. по возможности просьба донести как можно скорее или продлить срок

<b>==📖<u>{book_name}</u>📖==</b>
📖 автор: {author}
📁 id: {book_type_id}
Вернуть до: <b>{date_return:%d.%m.%Y}</b>
Куда: <b>{location_name} стелаж {shelf}, полка {row}</b>'''


notification_no_shelves = '''
ВНИМАНИЕ! Вы не вернули книгу. по возможности просьба донести как можно скорее или продлить срок

<b>==📖<u>{book_name}</u>📖==</b>
📖 автор: {author}
📁 id: {book_type_id}
Вернуть до: <b>{date_return:%d.%m.%Y}</b>
Куда: <b>{location_name}</b>'''


book_extended = '''
Книга продлена до {date_return:%d.%m.%Y} (2 недели)'''