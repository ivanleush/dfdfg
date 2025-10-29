from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder

def get_fortune_wheel_keyboard() -> types.InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        types.InlineKeyboardButton(
            text="🎡 Крутить колесо (1 раз в день)",
            callback_data="spin_wheel"
        )
    )
    builder.row(
        types.InlineKeyboardButton(
            text="📊 Статистика",
            callback_data="wheel_stats"
        ),
        types.InlineKeyboardButton(
            text="↩️ Назад",
            callback_data="back_to_menu"
        )
    )
    return builder.as_markup()