import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from app.database.models import Base
from app.database.session import engine

async def create_tables():
    """Создает все таблицы в базе данных."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Таблицы успешно созданы!")

async def init_db():
    """Инициализирует базу данных."""
    await create_tables()

if __name__ == "__main__":
    asyncio.run(init_db())