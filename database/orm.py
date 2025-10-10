from sqlalchemy import text, insert, select, or_, and_, BigInteger, cast, case, func, collate, delete, update
from database.core import async_engine, async_session_factory, Base
from database import models, core
from sqlalchemy.orm import selectinload, contains_eager, joinedload
import models as m
from itertools import groupby
from datetime import datetime, timedelta
from schemas import OperationType



async def create_table():
    async_engine.echo = False
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    async_engine.echo = False   


async def insert_data():
    async with async_session_factory() as session:
        session.add_all([
            models.LocationORM(location_name="Библиотека", description="Библиотека"),
            models.LocationORM(location_name="Буккросинг у Охраны", description="Буккросинг у Охраны"),
            models.BookTypeORM(book_name="Война и мир Том 1", author="Лев Толстой", positions=[
                models.BookORM(book_type_id=1, location_id=1, shelf=1, row=1),
                models.BookORM(book_type_id=1, location_id=1, shelf=2, row=2),
                models.BookORM(book_type_id=1, location_id=1, shelf=2, row=1),
                models.BookORM(book_type_id=1, location_id=1, shelf=1, row=1),
                models.BookORM(book_type_id=1, location_id=2),
                models.BookORM(book_type_id=1, location_id=2),
            ]),
            models.BookTypeORM(book_name="Война и мир Том 2", author="Лев Толстой", positions=[
                models.BookORM(book_type_id=1, location_id=1, shelf=1, row=1),
                models.BookORM(book_type_id=1, location_id=1, shelf=2, row=2),
            ]),
            models.BookTypeORM(book_name="Война и мир Том 3", author="Лев Толстой", positions=[
                models.BookORM(book_type_id=1, location_id=1, shelf=1, row=1),
                models.BookORM(book_type_id=1, location_id=1, shelf=2, row=2),
            ]),
            models.BookTypeORM(book_name="Война и мир Том 4", author="Лев Толстой", positions=[
                models.BookORM(book_type_id=1, location_id=1, shelf=1, row=1),
                models.BookORM(book_type_id=1, location_id=1, shelf=2, row=2),
            ]),
            models.BookTypeORM(book_name="Война и мир Том 5", author="Лев Толстой", positions=[
                models.BookORM(book_type_id=1, location_id=1, shelf=1, row=1),
                models.BookORM(book_type_id=1, location_id=1, shelf=2, row=2),
            ])
        ])
        await session.commit()


async def get_all_books():
    async with async_session_factory() as session:
        stmt = (
            select(
                models.BookTypeORM.book_type_id,
                models.BookTypeORM.book_name, 
                models.BookTypeORM.author
            )
            .join(models.BookTypeORM.positions)
            .where(models.BookORM.is_book_available == True)
            .order_by(models.BookTypeORM.book_name)
        )
        result = await session.execute(stmt)
        book_types = result.unique().all()
        return book_types


async def get_book_position(book_name) -> list[m.BookPosition]:
    async with async_session_factory() as session:

        stmt = (
            select(
                models.BookTypeORM.book_type_id,
                models.BookTypeORM.book_name, 
                models.BookTypeORM.author, 
                models.LocationORM.location_id,
                models.LocationORM.location_name,
                models.LocationORM.description,
                models.BookORM.shelf,
                models.BookORM.row,
                models.BookORM.is_book_available
            )
            .join(models.BookTypeORM.positions)
            .join(models.BookORM.location)
            .where(func.CASEFOLD(models.BookTypeORM.book_name).contains(func.CASEFOLD(book_name)))
            .where(models.BookORM.is_book_available == True)
        )
        result = await session.execute(stmt)
        books = result.all()
        books = list(map(m.RawBookPosition.model_validate, books))
        ans = []

        books = sorted(books, key=lambda x: (x.book_type_id, x.book_name, x.author))

        for book_data, book_group in groupby(books, lambda x: (x.book_type_id, x.book_name, x.author)):
            book_type_id, book_name, author = book_data

            book_group = sorted(book_group, key=lambda x: (x.location_name, x.description))

            locations = []
            for location_data, location_group in groupby(book_group, lambda x: (x.location_name, x.description, x.location_id)):
                location_name, description, location_id = location_data

                location_group = sorted(location_group, key=lambda x: (x.shelf, x.row))
                positions = []
                for position_data, books in groupby(location_group, lambda x: (x.shelf, x.row)):
                    shelf, row = position_data
                    print(shelf, row, location_name)
                    positions += [
                        m.Position(
                            shelf=shelf, 
                            row=row, 
                            amount=len(list(books))
                        )
                    ]
                
                locations += [
                    m.Location(
                        location_name=core.normalize_unicode(location_name), 
                        location_id=location_id,
                        description=core.normalize_unicode(description), 
                        positions=positions
                    )
                ]

            ans += [
                m.BookPosition(
                    book_type_id=book_type_id, 
                    book_name=core.normalize_unicode(book_name), 
                    author=core.normalize_unicode(author), 
                    locations=locations
                )
            ]
        return ans
            
        
        
async def select_book(book_type_id, location_id, shelf, row, user_id, user_name, date):
    async with async_session_factory() as session:

        stmt = (
            select(models.BookORM)
            .where(
                and_(
                    models.BookORM.book_type_id == book_type_id, 
                    models.BookORM.location_id == location_id, 
                    models.BookORM.shelf == shelf, 
                    models.BookORM.row == row,
                    models.BookORM.is_book_available == True
                )
            )
        )
        result = await session.execute(stmt)
        book: models.BookORM = result.scalars().first()
        book.is_book_available = False

        stmt = (select(models.UserORM).where(models.UserORM.tg_id == user_id))
        result = await session.execute(stmt)
        user: models.UserORM = result.scalars().first()
        if user is None:
            session.add(models.UserORM(tg_id=user_id, name=user_name))
            await session.commit()
            stmt = (select(models.UserORM).where(models.UserORM.tg_id == user_id))
            result = await session.execute(stmt)
            user: models.UserORM = result.scalars().first()

        session.add(
            models.ToReturnORM(
                book_id=book.book_id, 
                user_id=user.id, 
                date_start=date, 
                date_return=None, 
                last_notification=None
            )
        )
        

        session.add(
            models.HistoryORM(
                book_id=book.book_id,
                user_id=user.id, 
                date=date, 
                operation_type=OperationType.BORROW
            )
        )
        await session.commit()


async def get_all_borrowed_books(tg_id) -> list[m.BorrowedBook]:
    async with async_session_factory() as session:

        stmt = (
            select(
                models.BookORM.book_id,
                models.BookTypeORM.book_type_id,
                models.BookTypeORM.book_name, 
                models.BookTypeORM.author, 
                models.LocationORM.location_id,
                models.LocationORM.location_name,
                models.LocationORM.description,
                models.BookORM.shelf,
                models.BookORM.row,
                models.ToReturnORM.date_start,
                models.ToReturnORM.date_return
            )
            .join(models.ToReturnORM.book)  # JOIN BookORM
            .join(models.BookORM.book)  # JOIN BookTypeORM (добавлено)
            .join(models.BookORM.location)   # JOIN LocationORM
            .join(models.ToReturnORM.user)   # JOIN UserORM
            .where(models.UserORM.tg_id == tg_id)
        )
        result = await session.execute(stmt)
        borrowed_books = result.all()
        return list(map(m.BorrowedBook.model_validate, borrowed_books)) if borrowed_books else None


async def return_book(book_id, user_id):
    async with async_session_factory() as session:
        stmt = (select(models.UserORM).where(models.UserORM.tg_id == user_id))
        result = await session.execute(stmt)
        user: models.UserORM = result.scalars().first()
        
        stmt = (insert(models.HistoryORM).values(book_id=book_id, operation_type=OperationType.RETURN, user_id=user.id, date=datetime.now()))
        result = await session.execute(stmt)
        await session.commit()

        stmt = (delete(models.ToReturnORM).where(models.ToReturnORM.book_id == book_id).where(models.ToReturnORM.user_id == user.id))
        result = await session.execute(stmt)
        await session.commit()

        stmt = (update(models.BookORM).where(models.BookORM.book_id == book_id).values(is_book_available=True))
        result = await session.execute(stmt)
        await session.commit()


async def extend_book(book_id, user_id):
    async with async_session_factory() as session:
        stmt = (select(models.UserORM).where(models.UserORM.tg_id == user_id))
        result = await session.execute(stmt)
        user: models.UserORM = result.scalars().first()
        
        stmt = (insert(models.HistoryORM).values(book_id=book_id, operation_type=OperationType.EXTEND, user_id=user.id, date=datetime.now()))
        result = await session.execute(stmt)
        await session.commit()

        stmt = (update(models.ToReturnORM).where(models.ToReturnORM.book_id == book_id).where(models.ToReturnORM.user_id == user.id).values(date_return=datetime.now() + timedelta(weeks=2)))
        result = await session.execute(stmt)
        await session.commit()
    

async def get_notifications_data():
    
    async with async_session_factory() as session:
        stmt = (
            select(
                models.UserORM.tg_id,
                models.BookORM.book_id,
                models.BookTypeORM.book_type_id,
                models.BookTypeORM.book_name, 
                models.BookTypeORM.author, 
                models.LocationORM.location_id,
                models.LocationORM.location_name,
                models.LocationORM.description,
                models.BookORM.shelf,
                models.BookORM.row,
                models.ToReturnORM.date_start,
                models.ToReturnORM.date_return
            )
            .join(models.ToReturnORM.book)
            .join(models.BookORM.book)
            .join(models.BookORM.location)
            .join(models.ToReturnORM.user)
            .where(models.ToReturnORM.date_return <= datetime.now())
        )
        result = await session.execute(stmt)
        users = result.all()
        return list(map(m.NotificationData.model_validate, users)) if users else None