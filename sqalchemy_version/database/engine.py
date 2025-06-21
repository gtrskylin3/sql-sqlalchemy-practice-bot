from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from .models import Base

# Создаем асинхронный движок для SQLite
# sqlite+aiosqlite:/// - это URL для асинхронной работы с SQLite
# shop.db - имя файла базы данных
engine = create_async_engine("sqlite+aiosqlite:///shop.db", echo=True)

async_session = async_sessionmaker(
    engine, 
    class_=AsyncSession,
    expire_on_commit=False, # Не удалять объекты после коммита
    )

async def create_db():
    """
    Создает все таблицы в базе данных на основе моделей SQLAlchemy.
    """
    async with engine.begin() as conn:
        # Создаем все таблицы, определенные в моделях
        await conn.run_sync(Base.metadata.create_all)
    print("База данных и таблицы созданы успешно!")

async def get_session() -> AsyncSession:
    """
    Генератор для получения асинхронной сессии.
    Используется в middleware для передачи сессии в обработчики.
    """
    async with async_session() as session:
        yield session
