from database import orm
from asyncio import run
from app.bot import start_bot

if __name__ == "__main__":
    run(orm.create_table())
    run(orm.insert_data())
    print(run(orm.get_all_borrowed_books(5962717642)))
    # print(run(orm.get_book_position("война")))
    # print(run(orm.get_book_position(1)))
    start_bot()

