# Импорты для удобства
from . import (
    start, menu, subscription, balance, promocode,
    referral, support, common, fortune_wheel
)
from aiogram import Dispatcher
import logging

logger = logging.getLogger(__name__)


def setup_handlers(dp: Dispatcher):
    """Регистрация всех обработчиков"""
    logger.info("🔧 Начинаем регистрацию обработчиков...")

    # Регистрируем обработчики из каждого модуля
    start.register_handlers(dp)
    menu.register_handlers(dp)
    subscription.register_handlers(dp)
    balance.register_handlers(dp)
    promocode.register_handlers(dp)
    referral.register_handlers(dp)
    support.register_handlers(dp)
    common.register_handlers(dp)
    fortune_wheel.register_handlers(dp)

    logger.info("✅ Все обработчики зарегистрированы")