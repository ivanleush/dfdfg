import logging
from aiogram import Router, F, types, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ParseMode
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings
from app.database.crud.user import get_user_by_telegram_id, add_user_balance
from app.database.models import User
from app.states import WithdrawStates
from app.keyboards.inline import get_balance_keyboard

logger = logging.getLogger(__name__)
router = Router()

MIN_WITHDRAW_AMOUNT = 1000  # Минимальная сумма вывода в рублях

@router.callback_query(F.data == "withdraw_start")
async def withdraw_start_handler(callback: types.CallbackQuery, state: FSMContext, db: AsyncSession, db_user: User):
    """
    Обрабатывает нажатие на кнопку 'Вывести'.
    Проверяет баланс и запрашивает сумму.
    """
    balance_rub = db_user.balance_kopeks / 100

    # Проверяем баланс на соответствие минимальной сумме вывода
    if balance_rub < MIN_WITHDRAW_AMOUNT:
        await callback.answer(f"❌ Вывод средств доступен от {MIN_WITHDRAW_AMOUNT} рублей.", show_alert=True)
        return

    # Если баланс достаточен, запрашиваем сумму
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="↩️ Отмена", callback_data="cancel_withdraw")]
    ])
    await callback.message.edit_text(
        f"✅ Ваш текущий баланс: {balance_rub:.2f} рублей. \n\n"
        f"Введите сумму, которую хотите вывести (не меньше {MIN_WITHDRAW_AMOUNT} рублей):",
        reply_markup=keyboard
    )
    await state.set_state(WithdrawStates.get_amount)
    await callback.answer()


@router.message(WithdrawStates.get_amount)
async def process_amount(message: types.Message, state: FSMContext, db_user: User):
    """
    Обрабатывает введенную сумму.
    """
    balance_rub = db_user.balance_kopeks / 100

    try:
        amount_to_withdraw = float(message.text.replace(',', '.'))
        if amount_to_withdraw < MIN_WITHDRAW_AMOUNT:
            await message.answer(
                f"❌ Сумма для вывода должна быть не меньше {MIN_WITHDRAW_AMOUNT} рублей. Пожалуйста, введите другую сумму.")
            return
        if amount_to_withdraw > balance_rub:
            await message.answer(
                f"❌ На вашем балансе недостаточно средств. Ваш баланс: {balance_rub:.2f} рублей. Пожалуйста, введите другую сумму.")
            return

    except ValueError:
        await message.answer("❌ Неверный формат. Пожалуйста, введите сумму числом.")
        return

    # Сохраняем сумму в FSM и запрашиваем реквизиты
    await state.update_data(amount_to_withdraw=amount_to_withdraw)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="↩️ Отмена", callback_data="cancel_withdraw")]
    ])
    await message.answer(
        f"✅ Отлично, выводим {amount_to_withdraw:.2f} рублей. \n\n"
        "Теперь введите номер банковской карты или электронного кошелька, куда вы хотите вывести средства\n\n"
        "Важно! Вводите в формате\nБанк\nРеквизиты\n\nЕсли условия будут не соблюдены заявка будет отклонена",
        reply_markup=keyboard
    )
    await state.set_state(WithdrawStates.get_requisites)


@router.message(WithdrawStates.get_requisites)
async def process_requisites(message: types.Message, state: FSMContext, db: AsyncSession, db_user: User, bot: Bot):
    """
    Обрабатывает введенные пользователем реквизиты.
    """
    state_data = await state.get_data()
    amount_to_withdraw = state_data.get('amount_to_withdraw')
    requisites = message.text.strip()

    amount_kopeks = int(amount_to_withdraw * 100)

    success = await add_user_balance(db, db_user, -amount_kopeks, "Вывод средств")

    if not success:
        await message.answer("❌ Ошибка при списании средств. Обратитесь в поддержку.")
        return

    await db.commit()

    username = message.from_user.username if message.from_user.username else "Не указано"

    # Создаем заявку для админа, используя HTML
    admin_message_text = (
        f"<b>🚨 Новая заявка на вывод средств!</b>\n\n"
        f"<b>От пользователя:</b> @{username} (ID: <code>{db_user.id}</code>)\n"
        f"<b>Сумма к выводу:</b> {amount_to_withdraw:.2f} рублей\n"
        f"<b>Реквизиты:</b> <code>{requisites}</code>"
    )

    # Создаем кнопки для админа
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Принять",
                                 callback_data=f"withdraw_approve_{db_user.telegram_id}_{amount_to_withdraw}"),
            InlineKeyboardButton(text="❌ Отклонить",
                                 callback_data=f"withdraw_decline_{db_user.telegram_id}_{amount_to_withdraw}")
        ]
    ])

    # Отправляем уведомление админу
    await bot.send_message(
        chat_id=settings.ADMIN_IDS,
        text=admin_message_text,
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML
    )

    # Уведомляем пользователя
    await message.answer(
        "✅ Заявка на вывод средств создана и отправлена администратору. "
        "Сумма вывода была списана с вашего баланса. "
        "Ожидайте ответа в течение 24 часов."
    )

    # Очищаем состояние
    await state.clear()


@router.callback_query(F.data == "cancel_withdraw")
async def cancel_withdraw(callback: types.CallbackQuery, state: FSMContext):
    """
    Отменяет процесс вывода средств.
    """
    await state.clear()
    await callback.message.edit_text(
        "❌ Заявка на вывод средств отменена.",
        reply_markup=get_balance_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("withdraw_approve_"))
async def admin_approve_withdraw(callback: types.CallbackQuery, bot: Bot):
    """
    Админ принимает заявку на вывод.
    """
    if str(callback.from_user.id) != settings.ADMIN_IDS:
        return await callback.answer("Это действие доступно только администратору.", show_alert=True)

    _, _, telegram_id, amount_str = callback.data.split('_')
    telegram_id = int(telegram_id)  # ← это Telegram ID, а не ID базы
    amount_to_withdraw = float(amount_str)

    # Отправляем уведомление пользователю
    await bot.send_message(
        chat_id=telegram_id,  # ← используем Telegram ID
        text=f"✅ Ваша заявка на вывод средств в размере {amount_to_withdraw:.2f} рублей была одобрена. Средства будут отправлены в ближайшее время."
    )

    await callback.message.edit_text("✅ Заявка одобрена. Средства списаны с баланса пользователя.")
    await callback.answer()


@router.callback_query(F.data.startswith("withdraw_decline_"))
async def admin_decline_withdraw(callback: types.CallbackQuery, db: AsyncSession, bot: Bot):
    """
    Админ отклоняет заявку на вывод.
    """
    if str(callback.from_user.id) != settings.ADMIN_IDS:
        return await callback.answer("Это действие доступно только администратору.", show_alert=True)

    _, _, telegram_id, amount_str = callback.data.split('_')
    telegram_id = int(telegram_id)  # ← это Telegram ID
    amount_to_return = float(amount_str)

    # Находим пользователя по Telegram ID
    from app.database.crud.user import get_user_by_telegram_id
    user = await get_user_by_telegram_id(db, telegram_id)

    if not user:
        await callback.answer("❌ Пользователь не найден")
        return

    # Возвращаем деньги на баланс пользователя
    amount_kopeks = int(amount_to_return * 100)
    success = await add_user_balance(db, user, amount_kopeks, "Возврат средств при отклонении вывода")

    if not success:
        await callback.answer("❌ Ошибка при возврате средств")
        return

    await db.commit()

    # Отправляем уведомление пользователю
    await bot.send_message(
        chat_id=telegram_id,  # ← используем Telegram ID
        text=f"❌ Ваша заявка на вывод средств в размере {amount_to_return:.2f} рублей была отклонена. Средства возвращены на ваш баланс. Для уточнения причин, пожалуйста, свяжитесь с поддержкой."
    )

    await callback.message.edit_text("❌ Заявка отклонена. Средства возвращены на баланс пользователя.")
    await callback.answer()