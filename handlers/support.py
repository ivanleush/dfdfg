import logging
from aiogram import Dispatcher, types, F
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from app.config import settings
from app.database.models import User
from app.keyboards.inline import get_support_keyboard
from app.localization.texts import get_texts

logger = logging.getLogger(__name__)


async def show_support_info(
        callback: types.CallbackQuery,
        db_user: User
):
    texts = get_texts(db_user.language)

    await callback.message.edit_text(
        texts.SUPPORT_INFO,
        reply_markup=get_support_keyboard(db_user.language)
    )
    await callback.answer()


async def help_vpn_not_working(call: types.CallbackQuery):
    await call.message.delete()
    language = "ru"  # Нужно получить язык из пользователя
    texts = get_texts(language)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=texts.BACK, callback_data="help")]
    ])

    help_text = "🚫 Не работает VPN\n\n1️⃣ Проверьте, что у Вас стабильное интернет-соединение\n2️⃣ Попробуйте отключить и снова включить VPN\n3️⃣ Перезагрузите устройство \n\n🆘 Если проблема сохраняется, свяжитесь с поддержкой."

    await call.message.answer(text=help_text, reply_markup=keyboard)
    await call.answer()


async def help_instagram_not_working(call: types.CallbackQuery):
    await call.message.delete()
    language = "ru"
    texts = get_texts(language)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=texts.BACK, callback_data="help")]
    ])

    help_text = "📸 Не работает только Instagram\n\n❗ Это может быть связано с особенностями работы Instagram в некоторых регионах.\n\n1️⃣ Попробуйте переподключиться к VPN-серверу\n2️⃣ Обновите приложение Instagram до последней версии\n3️⃣ Очистите кэш приложения.\n\n🆘 Если ничего не помогает, обратитесь в поддержку."

    await call.message.answer(text=help_text, reply_markup=keyboard)
    await call.answer()


async def help_vpn_disconnects(call: types.CallbackQuery):
    await call.message.delete()
    language = "ru"
    texts = get_texts(language)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=texts.BACK, callback_data="help")]
    ])

    help_text = "🤪 VPN отключается сам по себе\n\n1️⃣ Убедитесь, что v2RayTun или другое используемое Вами приложение имеет необходимые разрешения на работу в фоновом режиме в настройках вашего устройства\n2️⃣ Попробуйте переключиться на другой сервер, если такая возможность доступна\n3️⃣ Проверьте, что на вашем устройстве достаточно оперативной памяти.\n\n🆘 Если проблема не решена, обратитесь в поддержку."
    await call.message.answer(text=help_text, reply_markup=keyboard)
    await call.answer()


async def help_support(call: types.CallbackQuery):
    await call.message.delete()
    language = "ru"
    texts = get_texts(language)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="Написать в техподдрежку",
                                 url=f"https://t.me/{settings.SUPPORT_USERNAME.lstrip('@')}")
        ],
        [InlineKeyboardButton(text=texts.BACK, callback_data="help")]
    ])

    help_text = "🆘Вы можете обратиться в нашу службу технической поддержки👇"
    await call.message.answer(text=help_text, reply_markup=keyboard)
    await call.answer()


async def help_back(call: types.CallbackQuery):
    """Обработчик для кнопки Назад в поддержке"""
    await call.message.delete()
    language = "ru"  # Нужно получить язык из пользователя
    texts = get_texts(language)

    keyboard = get_support_keyboard(language)
    await call.message.answer(text=texts.SUPPORT_INFO, reply_markup=keyboard)
    await call.answer()


def register_handlers(dp: Dispatcher):
    # Основное меню поддержки
    dp.callback_query.register(
        show_support_info,
        F.data == "menu_support"
    )

    # Обработчики конкретных вопросов поддержки
    dp.callback_query.register(
        help_vpn_not_working,
        F.data == "help_vpn_not_working"
    )

    dp.callback_query.register(
        help_instagram_not_working,
        F.data == "help_instagram_not_working"
    )

    dp.callback_query.register(
        help_vpn_disconnects,
        F.data == "help_vpn_disconnects"
    )

    dp.callback_query.register(
        help_support,
        F.data == "help_support"
    )

    dp.callback_query.register(
        help_back,
        F.data == "help"
    )

    # Обработчик возврата в меню (если нужно)
    dp.callback_query.register(
        help_back,
        F.data == "back_to_menu_from_support"
    )