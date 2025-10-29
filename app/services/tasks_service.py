import logging
from typing import List
from aiogram import Bot, Router, types, F
from aiogram.enums import ChatMemberStatus
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession
import html # Добавляем импорт для экранирования HTML

from app.database.crud.tasks import get_active_tasks, check_task_completion, complete_task, get_task_by_id
from app.database.crud.user import add_user_balance
from app.database.models import User, Task
from app.localization.texts import get_texts

logger = logging.getLogger(__name__)
router = Router()


class TasksService:
    async def get_available_tasks_text(self, db: AsyncSession, user_id: int) -> str:
        """Формирует текст со списком доступных заданий."""
        texts = get_texts('ru')
        active_tasks = await get_active_tasks(db)

        task_list_text = texts.TASKS_MENU_TITLE + "\n\n"

        for task in active_tasks:
            is_completed = await check_task_completion(db, user_id, task.id)
            status = "✅ Выполнено" if is_completed else "🔴 Не выполнено"

            # ✅ ИЗМЕНЕНИЕ: Генерируем "Канал 1", "Канал 2" и т.д.
            channels_list = ", ".join(
                f"<a href='{html.escape(c.url)}'>Канал {i + 1}</a>" for i, c in enumerate(task.channels))

            task_text = texts.TASK_TEMPLATE.format(
                title=html.escape(task.title),
                description=html.escape(task.description),
                reward_rubles=task.reward_kopeks / 100,
                channels_list=channels_list
            )
            task_list_text += f"▪️ {task_text}\n\n"

        return task_list_text

    async def check_subscription_and_reward(self, bot: Bot, db: AsyncSession, user: User, task: Task) -> bool:
        """Проверяет подписку на все каналы задания и начисляет награду."""
        # ✅ ИСПРАВЛЕНИЕ: Итерация по объектам TaskChannel
        for channel in task.channels:
            try:
                member = await bot.get_chat_member(chat_id=channel.channel_id, user_id=user.telegram_id)
                if member.status not in [ChatMemberStatus.MEMBER, ChatMemberStatus.ADMINISTRATOR,
                                         ChatMemberStatus.CREATOR]:
                    return False
            except Exception as e:
                logger.error(f"Не удалось проверить подписку на канал {channel.name}: {e}")
                return False

        await add_user_balance(db, user, task.reward_kopeks, f"Выполнение задания: {task.title}")
        await complete_task(db, user.telegram_id, task.id)

        return True


# Добавляем хэндлеры из второго файла
@router.callback_query(F.data == "tasks")
async def show_tasks(call: types.CallbackQuery, db: AsyncSession):
    """Отображает список доступных заданий."""
    tasks_service = TasksService()
    active_tasks = await get_active_tasks(db)
    user_id = call.from_user.id

    keyboard = InlineKeyboardBuilder()

    if active_tasks:
        for task in active_tasks:
            is_completed = await check_task_completion(db, user_id, task.id)
            if is_completed:
                button_text = f"✅ {html.escape(task.title)}"
            else:
                button_text = f"{html.escape(task.title)} ({task.reward_kopeks / 100}₽)"

            keyboard.row(types.InlineKeyboardButton(
                text=button_text,
                callback_data=f"show_task_{task.id}"
            ))
    else:
        await call.message.edit_text("Сейчас нет доступных заданий.")
        await call.answer()
        return

    # Кнопка назад
    keyboard.row(types.InlineKeyboardButton(text="↩️ Назад", callback_data="menu"))

    await call.message.edit_text(
        "Выберите задание:",
        reply_markup=keyboard.as_markup()
    )
    await call.answer()


@router.callback_query(F.data.startswith("check_task_"))
async def check_task_completion_handler(call: types.CallbackQuery, bot: Bot, db: AsyncSession):
    """
    Проверяет подписки и выдает вознаграждение.
    """
    task_id = int(call.data.split('_')[2])
    task = await get_task_by_id(db, task_id)
    user_id = call.from_user.id

    if not task:
        await call.answer("Задание не найдено.", show_alert=True)
        return

    if await check_task_completion(db, user_id, task_id):
        await call.answer("Вы уже выполнили это задание!", show_alert=True)
        return

    tasks_service = TasksService()

    # Получаем пользователя из базы данных (нужно добавить соответствующий метод в CRUD)
    user = User(telegram_id=user_id)  # Замените на реальное получение пользователя

    # Проверяем подписку и награждаем
    success = await tasks_service.check_subscription_and_reward(bot, db, user, task)

    if success:
        success_text = (
            f"✅ Поздравляем! Вы успешно выполнили задание и получили {task.reward_kopeks / 100}₽ на свой баланс."
        )
        await call.message.edit_text(success_text, parse_mode='HTML')
    else:
        # Формируем текст с каналами для подписки
        channels_text = ""
        # ✅ ИСПРАВЛЕНИЕ: Итерация по объектам TaskChannel
        if task.channels:
            for channel in task.channels:
                channels_text += f'<a href="{html.escape(channel.url)}">{html.escape(channel.name)}</a>\n'

        error_text = (
            "❌ Вы подписались не на все каналы. Пожалуйста, подпишитесь на следующие каналы и попробуйте снова:\n\n"
            f"{channels_text}"
        )

        # Кнопки для проверки
        keyboard = InlineKeyboardBuilder()
        keyboard.row(types.InlineKeyboardButton(
            text="Проверить выполнение ✅",
            callback_data=f"check_task_{task_id}"
        ))
        keyboard.row(types.InlineKeyboardButton(
            text="↩️ Назад к списку",
            callback_data="tasks"
        ))

        await call.message.edit_text(
            error_text,
            reply_markup=keyboard.as_markup(),
            parse_mode="HTML"
        )

    await call.answer()