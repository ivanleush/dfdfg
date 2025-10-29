import logging
from aiogram import Dispatcher, F, types, Bot, Router
from aiogram.enums import ParseMode
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from app.database.crud.tasks import get_active_tasks, get_task_by_id
from app.database.crud.task_completion import check_task_completion, create_task_completion
from app.database.crud.user import get_user_by_telegram_id, update_user_balance
from app.keyboards.inline import get_tasks_keyboard, get_main_menu_keyboard
from app.localization.texts import get_texts
from app.utils.decorators import error_handler
from app.services.tasks_service import TasksService
import html
from app.database.session import AsyncSessionLocal

logger = logging.getLogger(__name__)
router = Router()


def get_task_detail_keyboard(task_id: int, texts):
    """Создает клавиатуру для детального просмотра задания"""
    builder = InlineKeyboardBuilder()
    builder.add(
        InlineKeyboardButton(
            text=texts.CHECK_TASK_BUTTON,
            callback_data=f"check_task_{task_id}"
        )
    )
    builder.add(
        InlineKeyboardButton(
            text=texts.BACK_BUTTON,
            callback_data="tasks_menu"
        )
    )
    return builder.as_markup()


@router.callback_query(F.data == "tasks_menu")
async def tasks_menu_handler(callback: types.CallbackQuery, db: AsyncSession):
    """Обработчик меню заданий"""
    texts = get_texts(callback.from_user.language_code)
    tasks = await get_active_tasks(db)
    user_id = callback.from_user.id

    if not tasks:
        await callback.message.edit_text(
            html.escape(texts.NO_TASKS_AVAILABLE),
            reply_markup=get_main_menu_keyboard(texts),
            parse_mode=ParseMode.HTML
        )
        return

    completed_tasks = {}
    for task in tasks:
        is_completed = await check_task_completion(db, user_id, task.id)
        completed_tasks[task.id] = is_completed

    builder = InlineKeyboardBuilder()
    for task in tasks:
        if completed_tasks[task.id]:
            button_text = f"✅ {html.escape(task.title)}"
        else:
            button_text = f"{html.escape(task.title)} ({task.reward_kopeks / 100}₽)"

        builder.add(
            InlineKeyboardButton(
                text=button_text,
                callback_data=f"show_task_{task.id}"
            )
        )

    builder.add(
        InlineKeyboardButton(
            text="↩️ Назад",
            callback_data="back_to_menu"
        )
    )
    builder.adjust(1)

    await callback.message.edit_text(
        "Выберите задание:",
        reply_markup=builder.as_markup(),
        parse_mode=ParseMode.HTML
    )
    await callback.answer()


@router.callback_query(F.data.startswith("show_task_"))
async def show_single_task(callback: types.CallbackQuery):
    """Показывает информацию о конкретном задании."""
    try:
        async with AsyncSessionLocal() as db:
            texts = get_texts(callback.from_user.language_code)
            task_id = int(callback.data.split("_")[-1])
            task = await get_task_by_id(db, task_id)
            user_id = callback.from_user.id

            if not task:
                await callback.answer("❌ Задание не найдено.", show_alert=True)
                return

            is_completed = await check_task_completion(db, user_id, task.id)
            if is_completed:
                await callback.answer("Вы уже выполнили это задание!", show_alert=True)
                return

            reward = f"{task.reward_kopeks / 100:.2f}"

            channels_text = ""
            if task.channels:
                # Используем enumerate для получения индекса и объекта канала
                for i, channel in enumerate(task.channels):
                    channel_url = html.escape(channel.url)
                    # Формируем текст с номером канала и встраиваем ссылку
                    channels_text += f'<a href="{channel_url}">Подписаться {i + 1}</a>\n'

            message_text = (
                f"<b>Задание: {html.escape(task.title)}</b>\n\n"
                f"📝 <b>Описание:</b> {html.escape(task.description)}\n\n"
                f"💰 <b>Вознаграждение:</b> {reward} руб.\n\n"
                f"🔗 <b>Каналы для подписки:</b>\n\n"
                f"{channels_text}"
            )

            builder = InlineKeyboardBuilder()
            builder.add(
                InlineKeyboardButton(
                    text="Проверить выполнение ✅",
                    callback_data=f"check_task_{task.id}"
                )
            )
            builder.add(
                InlineKeyboardButton(
                    text="↩️ Назад к списку",
                    callback_data="tasks_menu"
                )
            )

            await callback.message.edit_text(
                message_text,
                reply_markup=builder.as_markup(),
                parse_mode=ParseMode.HTML,
                disable_web_page_preview=True
            )
            await callback.answer()

    except (ValueError, IndexError):
        await callback.answer("❌ Неверный формат данных.", show_alert=True)
    except Exception as e:
        logger.error(f"Ошибка в show_single_task: {e}")
        await callback.answer("❌ Произошла ошибка. Попробуйте позже.", show_alert=True)


@router.callback_query(F.data.startswith("check_task_"))
async def check_task_completion_handler(callback: types.CallbackQuery, bot: Bot, db: AsyncSession):
    """Проверяет подписки и выдает вознаграждение."""
    try:
        task_id = int(callback.data.split('_')[-1])
        user_id = callback.from_user.id
        texts = get_texts(callback.from_user.language_code)


        db_user = await get_user_by_telegram_id(db, user_id)
        if not db_user:
            await callback.answer("❌ Пользователь не найден.", show_alert=True)
            return

        task = await get_task_by_id(db, task_id)
        print(f"DEBUG: Type of task.channels is: {type(task.channels)}")
        print(f"DEBUG: Value of task.channels is: {task.channels}")

        # ✅ ИСПРАВЛЕНИЕ: Добавляем проверку, что task существует
        if not task:
            await callback.answer("❌ Задание не найдено.", show_alert=True)
            return

        is_completed = await check_task_completion(db, user_id, task.id)
        if is_completed:
            await callback.answer("✅ Вы уже выполнили это задание!", show_alert=True)
            return

        tasks_service = TasksService()
        is_subscribed = await tasks_service.check_subscription_and_reward(bot, db, db_user, task)

        if is_subscribed:
            success_text = (
                f"✅ Поздравляем! Вы успешно выполнили задание и получили {task.reward_kopeks / 100}₽ на свой баланс."
            )

            # ✅ ИЗМЕНЕНИЕ: Создаем клавиатуру с кнопкой "Главное меню"
            builder = InlineKeyboardBuilder()
            builder.add(
                InlineKeyboardButton(
                    text="↩️ Главное меню",
                    callback_data="back_to_menu"  # Убедитесь, что это правильный callback_data для главного меню
                )
            )

            await callback.message.edit_text(
                html.escape(success_text),
                reply_markup=builder.as_markup(),  # Передаем клавиатуру
                parse_mode=ParseMode.HTML
            )
        else:
            # ✅ ИСПРАВЛЕНИЕ: Вместо редактирования сообщения, отправляем всплывающее уведомление
            await callback.answer(
                "❌ Вы не подписались на все каналы. Пожалуйста, подпишитесь на них и попробуйте снова.",
                show_alert=True
            )

            builder = InlineKeyboardBuilder()
            builder.add(
                InlineKeyboardButton(
                    text="Проверить выполнение ✅",
                    callback_data=f"check_task_{task.id}"
                )
            )
            builder.add(
                InlineKeyboardButton(
                    text="↩️ Назад к списку",
                    callback_data="tasks_menu"
                )
            )

            await callback.message.edit_text(
                error_text,
                reply_markup=builder.as_markup(),
                parse_mode=ParseMode.HTML
            )

        await callback.answer()

    except Exception as e:
        logger.error(f"Ошибка в check_task_completion_handler: {e}")
        await callback.answer("❌ Произошла ошибка при проверке подписки", show_alert=True)

@router.callback_query(F.data == "back_to_tasks_list")
async def back_to_tasks_list_menu(callback: types.CallbackQuery, db: AsyncSession):
    """Возврат к списку заданий"""
    await tasks_menu_handler(callback, db)


def register_handlers(dp: Dispatcher):
    """Регистрация обработчиков"""
    dp.include_router(router)
    logger.info("✅ Обработчики заданий зарегистрированы")