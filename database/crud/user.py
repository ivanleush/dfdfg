import logging
import secrets
import string
from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
import logging
from datetime import datetime, timedelta
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.database.models import User
from typing import Dict, Any
from app.config import settings  # Измените config на settings


from app.database.models import User, UserStatus, Subscription, Transaction
from app.config import settings

logger = logging.getLogger(__name__)


def generate_referral_code() -> str:
    alphabet = string.ascii_letters + string.digits
    code_suffix = ''.join(secrets.choice(alphabet) for _ in range(8))
    return f"ref{code_suffix}"


async def get_user_by_id(db: AsyncSession, user_id: int) -> Optional[User]:
    result = await db.execute(
        select(User)
        .options(selectinload(User.subscription)) 
        .where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if user and user.subscription:
        _ = user.subscription.is_active
    
    return user


async def get_user_by_telegram_id(db: AsyncSession, telegram_id: int) -> Optional[User]:
    result = await db.execute(
        select(User)
        .options(selectinload(User.subscription)) 
        .where(User.telegram_id == telegram_id)
    )
    user = result.scalar_one_or_none()
    
    if user and user.subscription:
        _ = user.subscription.is_active
    
    return user


async def get_user_by_referral_code(db: AsyncSession, referral_code: str) -> Optional[User]:
    result = await db.execute(
        select(User).where(User.referral_code == referral_code)
    )
    return result.scalar_one_or_none()


async def create_unique_referral_code(db: AsyncSession) -> str:
    max_attempts = 10
    
    for _ in range(max_attempts):
        code = generate_referral_code()
        existing_user = await get_user_by_referral_code(db, code)
        if not existing_user:
            return code
    
    timestamp = str(int(datetime.utcnow().timestamp()))[-6:]
    return f"ref{timestamp}"


async def create_user(
    db: AsyncSession,
    telegram_id: int,
    username: str = None,
    first_name: str = None,
    last_name: str = None,
    language: str = "ru",
    referred_by_id: int = None,
    referral_code: str = None
) -> User:
    
    if not referral_code:
        from app.utils.user_utils import generate_unique_referral_code
        referral_code = await generate_unique_referral_code(db, telegram_id)
    
    user = User(
        telegram_id=telegram_id,
        username=username,
        first_name=first_name,
        last_name=last_name,
        language=language,
        referred_by_id=referred_by_id,
        referral_code=referral_code,
        balance_kopeks=0,
        has_had_paid_subscription=False,
        has_made_first_topup=False 
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    logger.info(f"✅ Создан пользователь {telegram_id} с реферальным кодом {referral_code}")
    
    return user


async def update_user_balance(db: AsyncSession, user_id: int, new_balance: float):
    """
    Обновляет баланс пользователя.
    """
    user = await get_user_by_telegram_id(db, user_id)
    if user:
        user.balance = new_balance
        await db.commit()
        await db.refresh(user)
        return user
    return None


async def update_user(
    db: AsyncSession,
    user: User = None,
    telegram_id: int = None,
    data_to_update: Dict[str, Any] = None,
    remnawave_uuid: Optional[str] = None,  # Явно добавляем этот параметр
    **kwargs
) -> Optional[User]:
    """
    Универсальная функция для обновления данных пользователя.
    
    :param db: Сессия базы данных
    :param user: Объект пользователя (опционально)
    :param telegram_id: ID пользователя в Telegram (опционально)
    :param data_to_update: Словарь с данными для обновления (опционально)
    :param remnawave_uuid: UUID пользователя в Remnawave (опционально)
    :param kwargs: Произвольные поля для обновления
    :return: Обновленный объект пользователя или None
    """
    # Получаем объект пользователя
    if user is None and telegram_id is not None:
        user = await get_user_by_telegram_id(db, telegram_id)
    
    if user is None:
        return None

    # Обновляем из data_to_update
    if data_to_update:
        for key, value in data_to_update.items():
            if hasattr(user, key):
                setattr(user, key, value)

    # Обновляем remnawave_uuid если передан
    if remnawave_uuid is not None:
        user.remnawave_uuid = remnawave_uuid

    # Обновляем из kwargs
    for field, value in kwargs.items():
        if hasattr(user, field):
            setattr(user, field, value)

    # Обновляем timestamp
    user.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(user)
    
    return user


async def get_remaining_cooldown(session: AsyncSession, user_id: int) -> int:
    """Возвращает оставшееся время кд в секундах"""
    result = await session.execute(
        select(User.wheel_last_used).where(User.telegram_id == user_id)
    )
    last_used = result.scalar_one_or_none()

    if not last_used:
        return 0

    cooldown_hours = settings.WHEEL_OF_FORTUNE_COOLDOWN_HOURS  # Используйте settings
    next_available = last_used + timedelta(hours=cooldown_hours)
    now = datetime.now()

    if now >= next_available:
        return 0

    return int((next_available - now).total_seconds())


async def add_balance(session: AsyncSession, user_id: int, amount: int) -> None:
    """Добавляет сумму к балансу пользователя"""
    await session.execute(
        update(User)
        .where(User.telegram_id == user_id)
        .values(balance_kopeks=User.balance_kopeks + amount * 100)
    )


async def set_wheel_cooldown(session: AsyncSession, user_id: int) -> None:
    """Устанавливает время последнего использования колеса"""
    await session.execute(
        update(User)
        .where(User.telegram_id == user_id)
        .values(wheel_last_used=datetime.now())
    )


async def add_user_balance(
    db: AsyncSession,
    user: User,
    amount_kopeks: int,
    description: str = "Пополнение баланса",
    create_transaction: bool = True,
    bot = None 
) -> bool:
    try:
        old_balance = user.balance_kopeks
        user.balance_kopeks += amount_kopeks
        user.updated_at = datetime.utcnow()
        
        if create_transaction:
            from app.database.crud.transaction import create_transaction as create_trans
            from app.database.models import TransactionType
            
            await create_trans(
                db=db,
                user_id=user.id,
                type=TransactionType.DEPOSIT,
                amount_kopeks=amount_kopeks,
                description=description
            )
        
        await db.commit()
        await db.refresh(user)
        
        
        logger.info(f"💰 Баланс пользователя {user.telegram_id} изменен: {old_balance} → {user.balance_kopeks} (изменение: +{amount_kopeks})")
        return True
        
    except Exception as e:
        logger.error(f"Ошибка изменения баланса пользователя {user.id}: {e}")
        await db.rollback()
        return False


async def add_user_balance_by_id(
    db: AsyncSession,
    telegram_id: int, 
    amount_kopeks: int,
    description: str = "Пополнение баланса"
) -> bool:
    try:
        user = await get_user_by_telegram_id(db, telegram_id)
        if not user:
            logger.error(f"Пользователь с telegram_id {telegram_id} не найден")
            return False
        
        return await add_user_balance(db, user, amount_kopeks, description)
        
    except Exception as e:
        logger.error(f"Ошибка пополнения баланса пользователя {telegram_id}: {e}")
        return False


async def subtract_user_balance(
    db: AsyncSession, 
    user: User, 
    amount_kopeks: int, 
    description: str
) -> bool:
    logger.error(f"💸 ОТЛАДКА subtract_user_balance:")
    logger.error(f"   👤 User ID: {user.id} (TG: {user.telegram_id})")
    logger.error(f"   💰 Баланс до списания: {user.balance_kopeks} копеек")
    logger.error(f"   💸 Сумма к списанию: {amount_kopeks} копеек")
    logger.error(f"   📝 Описание: {description}")
    
    if user.balance_kopeks < amount_kopeks:
        logger.error(f"   ❌ НЕДОСТАТОЧНО СРЕДСТВ!")
        return False
    
    try:
        old_balance = user.balance_kopeks
        user.balance_kopeks -= amount_kopeks
        user.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(user)
        
        logger.error(f"   ✅ Средства списаны: {old_balance} → {user.balance_kopeks}")
        return True
        
    except Exception as e:
        logger.error(f"   ❌ ОШИБКА СПИСАНИЯ: {e}")
        await db.rollback()
        return False


async def get_users_list(
    db: AsyncSession,
    offset: int = 0,
    limit: int = 50,
    search: Optional[str] = None,
    status: Optional[UserStatus] = None
) -> List[User]:
    
    query = select(User).options(selectinload(User.subscription))
    
    if status:
        query = query.where(User.status == status.value)
    
    if search:
        search_term = f"%{search}%"
        conditions = [
            User.first_name.ilike(search_term),
            User.last_name.ilike(search_term),
            User.username.ilike(search_term)
        ]
        
        if search.isdigit():
            conditions.append(User.telegram_id == int(search))
        
        query = query.where(or_(*conditions))
    
    query = query.order_by(User.created_at.desc()).offset(offset).limit(limit)
    
    result = await db.execute(query)
    return result.scalars().all()


async def get_users_count(
    db: AsyncSession,
    status: Optional[UserStatus] = None,
    search: Optional[str] = None
) -> int:
    
    query = select(func.count(User.id))
    
    if status:
        query = query.where(User.status == status.value)
    
    if search:
        search_term = f"%{search}%"
        conditions = [
            User.first_name.ilike(search_term),
            User.last_name.ilike(search_term),
            User.username.ilike(search_term)
        ]
        
        if search.isdigit():
            conditions.append(User.telegram_id == int(search))
        
        query = query.where(or_(*conditions))
    
    result = await db.execute(query)
    return result.scalar()


async def get_referrals(db: AsyncSession, user_id: int) -> List[User]:
    result = await db.execute(
        select(User)
        .options(selectinload(User.subscription))
        .where(User.referred_by_id == user_id)
        .order_by(User.created_at.desc())
    )
    return result.scalars().all()


async def get_inactive_users(db: AsyncSession, months: int = 3) -> List[User]:
    threshold_date = datetime.utcnow() - timedelta(days=months * 30)
    
    result = await db.execute(
        select(User)
        .options(selectinload(User.subscription))
        .where(
            and_(
                User.last_activity < threshold_date,
                User.status == UserStatus.ACTIVE.value
            )
        )
    )
    return result.scalars().all()


async def delete_user(db: AsyncSession, user: User) -> bool:
    user.status = UserStatus.DELETED.value
    user.updated_at = datetime.utcnow()
    
    await db.commit()
    logger.info(f"🗑️ Пользователь {user.telegram_id} помечен как удаленный")
    return True


async def get_users_statistics(db: AsyncSession) -> dict:
    
    total_result = await db.execute(select(func.count(User.id)))
    total_users = total_result.scalar()
    
    active_result = await db.execute(
        select(func.count(User.id)).where(User.status == UserStatus.ACTIVE.value)
    )
    active_users = active_result.scalar()
    
    today = datetime.utcnow().date()
    today_result = await db.execute(
        select(func.count(User.id)).where(
            and_(
                User.created_at >= today,
                User.status == UserStatus.ACTIVE.value
            )
        )
    )
    new_today = today_result.scalar()
    
    week_ago = datetime.utcnow() - timedelta(days=7)
    week_result = await db.execute(
        select(func.count(User.id)).where(
            and_(
                User.created_at >= week_ago,
                User.status == UserStatus.ACTIVE.value
            )
        )
    )
    new_week = week_result.scalar()
    
    month_ago = datetime.utcnow() - timedelta(days=30)
    month_result = await db.execute(
        select(func.count(User.id)).where(
            and_(
                User.created_at >= month_ago,
                User.status == UserStatus.ACTIVE.value
            )
        )
    )
    new_month = month_result.scalar()
    
    return {
        "total_users": total_users,
        "active_users": active_users,
        "blocked_users": total_users - active_users,
        "new_today": new_today,
        "new_week": new_week,
        "new_month": new_month
    }
