import models as m


def find_book(book_type_id, books: list[m.BookPosition]):
    for book in books:
        if book.book_type_id == int(book_type_id):
            return book
        

def find_location(location_id, book: m.BookPosition):
    for location in book.locations:
        if location.location_id == int(location_id):
            return location


def find_book_by_id(book_type_id, books: list[m.BookPosition]):
    for book in books:
        if book.book_type_id == int(book_type_id):
            return book


def find_book_by_local_id(book_id, books: list[m.BookPosition]):
    for book in books:
        if book.book_id == int(book_id):
            return book