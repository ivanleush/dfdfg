import logging
from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from app.states import PromoCodeStates
from app.database.database import get_db
from app.database.crud.user import get_user_by_telegram_id
from app.keyboards.inline import get_back_keyboard
from app.localization.texts import get_texts
from app.services.promocode_service import PromoCodeService
from app.utils.decorators import error_handler
from app.database.models import User

logger = logging.getLogger(__name__)

router = Router()


def register_handlers(dp: Router):
    """Регистрирует все обработчики промокодов."""
    dp.include_router(router)
    logger.info("✅ Обработчики промокодов зарегистрированы")


@router.callback_query(F.data == "show_promocode")
@error_handler
async def show_promocode_menu(
        callback: types.CallbackQuery,
        state: FSMContext,
):
    async for db in get_db():
        db_user = await get_user_by_telegram_id(db, callback.from_user.id)
        if not db_user:
            await callback.answer("Ваш профиль не найден.", show_alert=True)
            return

        texts = get_texts(db_user.language)

        await callback.message.edit_text(
            texts.PROMOCODE_ENTER,
            reply_markup=get_back_keyboard(db_user.language)
        )

        await state.set_state(PromoCodeStates.waiting_for_code)
        await callback.answer()


@router.message(PromoCodeStates.waiting_for_code)
@error_handler
async def process_promocode(
        message: types.Message,
        state: FSMContext,
):
    async for db in get_db():
        db_user = await get_user_by_telegram_id(db, message.from_user.id)
        if not db_user:
            await message.answer("Пользователь не найден.")
            await state.clear()
            return

        texts = get_texts(db_user.language)
        code = message.text.strip()

        if not code:
            await message.answer(
                "❌ Введите корректный промокод",
                reply_markup=get_back_keyboard(db_user.language)
            )
            return

        promocode_service = PromoCodeService()
        result = await promocode_service.activate_promocode(db, db_user.id, code)

        if result["success"]:
            await message.answer(
                texts.PROMOCODE_SUCCESS.format(description=result["description"]),
                reply_markup=get_back_keyboard(db_user.language)
            )
            logger.info(f"✅ Пользователь {db_user.telegram_id} активировал промокод {code}")
        else:
            error_messages = {
                "not_found": texts.PROMOCODE_INVALID,
                "expired": texts.PROMOCODE_EXPIRED,
                "used": texts.PROMOCODE_USED,
                "already_used_by_user": texts.PROMOCODE_USED,
                "server_error": texts.ERROR
            }

            error_text = error_messages.get(result["error"], texts.PROMOCODE_INVALID)
            await message.answer(
                error_text,
                reply_markup=get_back_keyboard(db_user.language)
            )

        await state.clear()