from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy import String, event
from config import settings
from typing import Annotated

# асинхронный движоек
async_engine = create_async_engine(
    url=settings.db_url,
    echo=True,  # выключение логов
    pool_size=5,
    max_overflow=10,
    connect_args={"check_same_thread": False}
)

# Дополнительная настройка через event
@event.listens_for(async_engine.sync_engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA encoding = 'UTF-8'")
    cursor.execute("PRAGMA case_sensitive_like = ON")
    cursor.close()

# как бы исполнитель запросов
async_session_factory = sessionmaker(
    async_engine,
    expire_on_commit=False,
    class_=AsyncSession
)

# дополнительный класс данных для бд
str_256 = Annotated[str, 256]


class Base(DeclarativeBase):
    # добавляем аннотации
    type_annotation_map = {
        str_256: String(256),
    }

    repr_columns_num = 200
    repr_cols = tuple()

    def __repr__(self):  # переделка принта моделей в логах
        cols = []
        for idx, col in enumerate(self.__table__.columns.keys()):
            if col in self.repr_cols or idx < self.repr_columns_num:
                cols.append(f"{col}={getattr(self, col)}")
        return f"{self.__class__.__name__}({', '.join(cols)})"


# вставь это в ваш existing файл (заменяет/дополняет обработчик connect)
from sqlalchemy import event, text, func
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# ... твоя конфигурация async_engine, async_session_factory и Base остаются
import unicodedata
def normalize_unicode(text):
    """Нормализует Unicode строку к форме NFC"""
    return unicodedata.normalize('NFC', text)



def _casefold_py(s):
    return normalize_unicode(s).casefold() if s is not None else None

@event.listens_for(async_engine.sync_engine, "connect")
def _register_casefold(dbapi_connection, connection_record):
    """
    Попытки зарегистрировать CASEFOLD на первом доступном объекте,
    т.к. у обёртки aiosqlite может не быть create_collation.
    """
    # пробуем разные места, где может быть метод create_function
    candidates = (
        dbapi_connection,
        getattr(dbapi_connection, "connection", None),   # часто для адаптеров
        getattr(dbapi_connection, "_conn", None),        # иногда внутреннее поле
        getattr(dbapi_connection, "raw_connection", None)
    )

    for conn in candidates:
        if conn is None:
            continue
        if hasattr(conn, "create_function"):
            # Регистрируем именованную SQL-функцию CASEFOLD
            conn.create_function("CASEFOLD", 1, _casefold_py)
            # не регистрируем колляцию, т.к. мало шансов, что есть create_collation
            return

    # если ни у кого нет create_function — сообщаем (но не падаем)
    # можно заменить принт на логгер
    print("WARN: не удалось зарегистрировать CASEFOLD — у соединения нет create_function()")
