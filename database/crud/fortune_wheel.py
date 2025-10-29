from sqlalchemy import select, func, Integer
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import FortuneWheelSpin

async def create_fortune_wheel_spin(
    db: AsyncSession,
    user_id: int,
    amount_kopeks: int,
    is_win: bool
) -> FortuneWheelSpin:
    spin = FortuneWheelSpin(
        user_id=user_id,
        amount_kopeks=amount_kopeks,
        is_win=is_win
    )
    db.add(spin)
    await db.commit()
    await db.refresh(spin)
    return spin

async def get_last_spin_time(db: AsyncSession, user_id: int):
    result = await db.execute(
        select(FortuneWheelSpin.created_at)
        .where(FortuneWheelSpin.user_id == user_id)
        .order_by(FortuneWheelSpin.created_at.desc())
        .limit(1)  # ДОБАВЛЕНО ограничение
    )
    return result.scalar_one_or_none()

async def get_fortune_wheel_stats(db: AsyncSession, user_id: int):
    result = await db.execute(
        select(
            func.count(FortuneWheelSpin.id).label("total_spins"),
            func.sum(FortuneWheelSpin.is_win.cast(Integer)).label("wins")
        )
        .where(FortuneWheelSpin.user_id == user_id)
    )
    # ИЗМЕНЕНО: используем one_or_none() вместо first()
    return result.one_or_none()

async def get_user_total_winnings(db: AsyncSession, user_id: int):
    result = await db.execute(
        select(func.coalesce(func.sum(FortuneWheelSpin.amount_kopeks), 0))
        .where(FortuneWheelSpin.user_id == user_id)
    )
    return result.scalar()
