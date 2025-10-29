# Стандартные библиотеки
import logging
import os

# Сторонние библиотеки
from aiogram import Router, F, types, Bot
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile
from sqlalchemy.ext.asyncio import AsyncSession

# Локальные модули
from app.config import settings
from app.database.crud.user import get_user_by_telegram_id
from app.database.database import get_db
from app.database.models import User
from app.keyboards.inline import (
    get_back_keyboard,
    get_profile_keyboard,
    get_documents_keyboard,
)
from app.localization.texts import get_texts
from app.services.promocode_service import PromoCodeService
from app.services.user_profile_service import UserProfileService
from app.states import PromoCodeStates
from app.utils.decorators import error_handler

from app.handlers import (
    start, menu, subscription, balance,
    referral, support, common,
    profile_handlers,
    promocode_handlers, # ✅ Должен быть в этом списке
    tasks_handlers,
    fortune_wheel
)

from app.handlers.admin import (
    main as admin_main, users as admin_users, subscriptions as admin_subscriptions,
    promocodes as admin_promocodes, messages as admin_messages,
    monitoring as admin_monitoring, referrals as admin_referrals,
    rules as admin_rules, remnawave as admin_remnawave,
    statistics as admin_statistics, user_messages as admin_user_messages,
    version as admin_version, servers as admin_servers,
    maintenance as admin_maintenance
)

logger = logging.getLogger(__name__)
router = Router()


def register_handlers(dp: Router):
    """Регистрирует обработчики профиля в диспетчере."""
    dp.include_router(router)
    logger.info("✅ Обработчики профиля зарегистрированы")


@router.callback_query(F.data == "show_profile")
@error_handler
async def show_profile_menu(callback: types.CallbackQuery):
    """Отображает меню профиля пользователя."""
    async for db in get_db():
        user = await get_user_by_telegram_id(db, callback.from_user.id)
        if not user:
            return

        texts = get_texts(user.language)

        # Проверяем, есть ли у пользователя юзернейм
        if user.username:
            username_text = f"<b>Профиль</b> @{user.username}\n\n"
        else:
            username_text = "" # Если юзернейма нет, оставляем строку пустой

        message_text = (
            f"{username_text}" # Добавляем строку с юзернеймом
            f"<b>Ваш ID:</b> <code>{user.telegram_id}</code>\n"
            f"<b>{texts.BALANCE_MESSAGE.format(balance=user.balance_kopeks / 100)}</b>\n\n"
        )
        await callback.message.edit_text(
            message_text,
            reply_markup=get_profile_keyboard(texts),
            parse_mode=ParseMode.HTML,
        )
        await callback.answer()


@router.callback_query(F.data == "show_documents")
@error_handler
async def show_documents_menu(callback: types.CallbackQuery):
    async for db in get_db():
        user = await get_user_by_telegram_id(db, callback.from_user.id)
        if not user: return

        texts = get_texts(user.language)

        await callback.message.edit_text(
            texts.DOCUMENTS_MENU_TITLE,
            reply_markup=get_documents_keyboard(texts),
            parse_mode=ParseMode.HTML
        )
        await callback.answer()


project_root = os.getcwd()

# Путь к файлам относительно корня проекта
file_path_support = os.path.join(project_root, "Контакты поддержки.pdf")
file_path_privacy = os.path.join(project_root, "Политика конфиденциальности.pdf")
file_path_terms = os.path.join(project_root, "Пользовательское соглашение.pdf")


# Функция для отправки файла
async def send_file(callback: types.CallbackQuery, bot: Bot, file_path: str):
    if not os.path.exists(file_path):
        await callback.answer(f"Не удалось найти файл по пути: {file_path}", show_alert=True)
        return

    try:
        pdf_file = FSInputFile(file_path)
        await bot.send_document(chat_id=callback.message.chat.id, document=pdf_file)
        await callback.answer()
    except Exception as e:
        await callback.answer(f"Не удалось отправить файл. Ошибка: {e}", show_alert=True)


# Обработчики для отправки документов
@router.callback_query(F.data == "send_document_support")
@error_handler
async def send_support_doc(callback: types.CallbackQuery, bot: Bot):
    await send_file(callback, bot, file_path_support)


@router.callback_query(F.data == "send_document_privacy_policy")
@error_handler
async def send_privacy_doc(callback: types.CallbackQuery, bot: Bot):
    await send_file(callback, bot, file_path_privacy)


@router.callback_query(F.data == "send_document_terms_of_service")
@error_handler
async def send_agreement_doc(callback: types.CallbackQuery, bot: Bot):
    await send_file(callback, bot, file_path_terms)


@router.callback_query(F.data == "back_to_profile")
@error_handler
async def back_to_profile_menu(callback: types.CallbackQuery):
    await show_profile_menu(callback)

@router.callback_query(F.data == "show_promocode_menu")
@error_handler
async def show_promocode_menu(callback: types.CallbackQuery, db_user: User, state: FSMContext):
    texts = get_texts(db_user.language)
    await callback.message.edit_text(
        texts.PROMOCODE_ENTER, reply_markup=get_back_keyboard(db_user.language)
    )
    await state.set_state(PromoCodeStates.waiting_for_code)
    await callback.answer()


@router.message(PromoCodeStates.waiting_for_code)
@error_handler
async def process_promocode(
    message: types.Message, db_user: User, state: FSMContext, db: AsyncSession
):
    texts = get_texts(db_user.language)
    code = message.text.strip()
    if not code:
        await message.answer(
            "❌ Введите корректный промокод",
            reply_markup=get_back_keyboard(db_user.language),
        )
        return

    promocode_service = PromoCodeService()
    result = await promocode_service.activate_promocode(db, db_user.id, code)

    if result["success"]:
        await message.answer(
            texts.PROMOCODE_SUCCESS.format(description=result["description"]),
            reply_markup=get_back_keyboard(db_user.language),
        )
        logger.info(f"✅ Пользователь {db_user.telegram_id} активировал промокод {code}")
    else:
        error_messages = {
            "not_found": texts.PROMOCODE_INVALID,
            "expired": texts.PROMOCODE_EXPIRED,
            "used": texts.PROMOCODE_USED,
            "already_used_by_user": texts.PROMOCODE_USED,
            "server_error": texts.ERROR,
        }
        error_text = error_messages.get(result["error"], texts.PROMOCODE_INVALID)
        await message.answer(error_text, reply_markup=get_back_keyboard(db_user.language))

    await state.clear()