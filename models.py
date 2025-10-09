from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from datetime import datetime


class OrmModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class Position(BaseModel):
    shelf: Optional[int]
    row: Optional[int]
    amount: int

class Location(BaseModel):
    location_id: int
    location_name: str
    description: str
    positions: list[Position]

class BookPosition(BaseModel):
    book_type_id: int
    book_name: str
    author: str
    locations: list[Location]
    

class RawBookPosition(OrmModel):
    book_type_id: int
    book_name: str
    author: str
    location_id: int
    location_name: str
    description: str
    shelf: Optional[int]
    row: Optional[int]
    is_book_available: Optional[bool] = False


class BorrowedBook(RawBookPosition):
    book_id: int
    date_start: datetime
    date_return: datetime


class NotificationData(BorrowedBook):
    tg_id: int