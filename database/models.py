from sqlalchemy.orm import Mapped, mapped_column, relationship
from database.core import Base
from typing import Optional
from sqlalchemy import ForeignKey, String
from datetime import datetime, timedelta
from schemas import OperationType


class BookTypeORM(Base):
    __tablename__ = "book_type"

    book_type_id: Mapped[int] = mapped_column(primary_key=True)
    book_name: Mapped[str] = mapped_column(String(collation="BINARY"))
    author: Mapped[str] = mapped_column(String(collation="BINARY"))

    positions: Mapped[list["BookORM"]] = relationship(back_populates="book")


class LocationORM(Base):
    __tablename__ = "location"

    location_id: Mapped[int] = mapped_column(primary_key=True)
    location_name: Mapped[str]
    description: Mapped[str]

    positions: Mapped[list["BookORM"]] = relationship(back_populates="location")


class BookORM(Base):
    __tablename__ = "book"

    book_id: Mapped[int] = mapped_column(primary_key=True)
    book_type_id: Mapped[int] = mapped_column(ForeignKey(BookTypeORM.book_type_id))
    location_id: Mapped[int] = mapped_column(ForeignKey(LocationORM.location_id))
    shelf: Mapped[Optional[int]]
    row: Mapped[Optional[int]]
    is_book_available: Mapped[bool] = mapped_column(default=True)

    book: Mapped["BookTypeORM"] = relationship(back_populates="positions")
    location: Mapped["LocationORM"] = relationship(back_populates="positions")
    history: Mapped[list["HistoryORM"]] = relationship(back_populates="book")
    to_return: Mapped[list["ToReturnORM"]] = relationship(back_populates="book")


class UserORM(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int]
    name: Mapped[str]

    history: Mapped[list["HistoryORM"]] = relationship(back_populates="user")
    to_return: Mapped[list["ToReturnORM"]] = relationship(back_populates="user")


class HistoryORM(Base):
    __tablename__ = "history"

    id: Mapped[int] = mapped_column(primary_key=True)
    book_id: Mapped[int] = mapped_column(ForeignKey(BookORM.book_id))
    date: Mapped[datetime]
    user_id: Mapped[int] = mapped_column(ForeignKey(UserORM.id))
    operation_type: Mapped[OperationType]
    
    user: Mapped["UserORM"] = relationship(back_populates="history")
    book: Mapped["BookORM"] = relationship(back_populates="history")


class ToReturnORM(Base):
    __tablename__ = "to_return"

    id: Mapped[int] = mapped_column(primary_key=True)
    book_id: Mapped[int] = mapped_column(ForeignKey(BookORM.book_id))
    user_id: Mapped[int] = mapped_column(ForeignKey(UserORM.id))
    date_start: Mapped[datetime]
    date_return: Mapped[Optional[datetime]]
    last_notification: Mapped[Optional[datetime]]

    user: Mapped["UserORM"] = relationship(back_populates="to_return")
    book: Mapped["BookORM"] = relationship(back_populates="to_return")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.date_start and not self.date_return:
            self.date_return = self.date_start + timedelta(weeks=2)