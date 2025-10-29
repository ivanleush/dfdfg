import random
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional
from aiogram import types
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.crud.user import add_user_balance, get_user_by_telegram_id
from app.database.crud.fortune_wheel import (
    create_fortune_wheel_spin,
    get_last_spin_time,
    get_fortune_wheel_stats,
    get_user_total_winnings
)
from app.config import settings
from app.localization.texts import get_texts

logger = logging.getLogger(__name__)


class FortuneWheelService:
    async def spin_wheel(
            self,
            db: AsyncSession,
            user: types.User,
            message: types.Message
    ) -> dict:
        """
        Обрабатывает спин колеса фортуны для пользователя.
        Возвращает словарь с результатом.
        """
        # Проверяем, когда пользователь последний раз крутил колесо
        last_spin = await get_last_spin_time(db, user.id)

        # Проверяем, прошло ли 24 часа с последнего спина
        if last_spin and last_spin > datetime.utcnow() - timedelta(hours=24):
            time_left = last_spin + timedelta(hours=24) - datetime.utcnow()
            hours = time_left.seconds // 3600
            minutes = (time_left.seconds % 3600) // 60

            return {
                "success": False,
                "message": f"⏳ Вы сможете крутить колесо снова через {hours}ч {minutes}м"
            }

        # Отправляем анимацию вращения
        animation_message = await message.answer("🎡 Колесо вращается...")

        # Задержка для имитации вращения
        await asyncio.sleep(2)

        # Удаляем сообщение с анимацией, оборачиваем в try-except на случай ошибки
        try:
            await animation_message.delete()
        except Exception as e:
            logger.warning(f"Не удалось удалить сообщение анимации: {e}")

        # Определяем выигрыш
        win_amount = self._get_random_win_amount()

        # Записываем результат спина в базу данных
        spin = await create_fortune_wheel_spin(
            db,
            user_id=user.id,
            amount_kopeks=win_amount,
            is_win=win_amount > 0
        )

        # Начисляем выигрыш на баланс, если он есть
        if win_amount > 0:
            # Получаем актуальный объект пользователя из БД
            user_db = await get_user_by_telegram_id(db, user.id)
            if user_db:
                await add_user_balance(
                    db,
                    user_db,
                    win_amount,
                    f"Выигрыш в колесе фортуны #{spin.id}"
                )
            else:
                logger.error(f"Пользователь с ID {user.id} не найден при начислении выигрыша.")

        win_text = self._get_win_text(win_amount)

        return {
            "success": True,
            "amount": win_amount,
            "message": win_text
        }

    def _get_random_win_amount(self) -> int:
        """
        Определяет случайный выигрыш на основе вероятностей.
        Выигрыш в копейках.
        """
        outcomes = settings.FORTUNE_WHEEL_OUTCOMES
        weights = [outcome['weight'] for outcome in outcomes]

        selected_outcome = random.choices(outcomes, weights=weights, k=1)[0]

        min_amount = selected_outcome['min_amount_kopeks']
        max_amount = selected_outcome['max_amount_kopeks']

        return random.randint(min_amount, max_amount)

    def _get_win_text(self, amount_kopeks: int) -> str:
        """
        Возвращает текстовое сообщение о выигрыше.
        """
        texts = get_texts('ru')  # Здесь можно передавать язык из контекста, если нужно
        rubles = amount_kopeks / 100

        if amount_kopeks == 0:
            return texts.FORTUNE_WHEEL_LOSE

        return random.choice(texts.FORTUNE_WHEEL_WIN.split(" | ")).format(rubles=rubles)

    async def get_stats(self, db: AsyncSession, user_id: int) -> dict:
        """
        Получает и возвращает статистику колеса фортуны для пользователя.
        """
        stats = await get_fortune_wheel_stats(db, user_id)
        total_winnings = await get_user_total_winnings(db, user_id)

        return {
            "total_spins": stats.total_spins if stats else 0,
            "wins": stats.wins if stats else 0,
            "total_winnings": total_winnings if total_winnings else 0
        }