from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
import os

# Используем переменную окружения или значение по умолчанию
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./bot.db")

# Создаем асинхронный движок
engine = create_async_engine(DATABASE_URL, echo=True)

# Создаем фабрику сессий
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

async def get_db():
    """Генератор сессий БД для Dependency Injection."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()