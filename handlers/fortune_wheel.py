from aiogram import Router, F, types
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.database.database import get_db
from app.services.fortune_wheel_service import FortuneWheelService
from app.handlers.keyboards import get_fortune_wheel_keyboard
from sqlalchemy import select, func, Integer
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import FortuneWheelSpin

logger = logging.getLogger(__name__)
logger.info("Модуль fortune_wheel загружен")
router = Router() # ✅ ДОБАВЬТЕ ЭТУ СТРОКУ


@router.callback_query(F.data == "fortune_wheel")
async def show_fortune_wheel(callback: types.CallbackQuery):
    logger.info(f"Обработчик колеса фортуны вызван пользователем {callback.from_user.id}")
    await callback.message.edit_text(
        "🎡 Колесо фортуны\n\nКаждый день вы можете крутить колесо и выигрывать до 50 рублей!",
        reply_markup=get_fortune_wheel_keyboard()
    )


@router.callback_query(F.data == "spin_wheel")
async def spin_fortune_wheel(callback: types.CallbackQuery, db: AsyncSession):
    try:
        service = FortuneWheelService()
        result = await service.spin_wheel(db, callback.from_user, callback.message)

        if result["success"]:
            await callback.answer()  # Отправляем пустой ответ на callback
            await callback.message.answer(
                result["message"]
            )
            # Успешно, больше ничего не делаем с предыдущим сообщением

        else:
            # Пользователь уже крутил колесо
            await callback.answer(result["message"], show_alert=True)
            # Здесь ничего не редактируем, так как сообщение уже в нужном состоянии

    except Exception as e:
        logger.error(f"Ошибка в spin_fortune_wheel: {e}")
        await callback.answer("Произошла ошибка при обработке запроса", show_alert=True)


@router.callback_query(F.data == "wheel_stats")
async def show_wheel_stats(callback: types.CallbackQuery):
    try:
        async for db in get_db():
            service = FortuneWheelService()
            stats = await service.get_stats(db, callback.from_user.id)

        total_winnings_kopeks = stats.get('total_winnings', 0)
        total_winnings_rubles = total_winnings_kopeks / 100

        await callback.message.answer(
            f"📊 Ваша статистика колеса фортуны:\n\n"
            f"• Всего спинов: {stats['total_spins']}\n"
            f"• Побед: {stats['wins']}\n"
            f"• Общий выигрыш: {total_winnings_rubles:.2f} ₽"
        )
    except Exception as e:
        logger.error(f"Ошибка в show_wheel_stats: {e}")
        await callback.answer("Произошла ошибка при получении статистики", show_alert=True)

def register_handlers(dp):
    """Регистрация обработчиков"""
    dp.include_router(router)
    logger.info("✅ Обработчики колеса фортуны зарегистрированы")