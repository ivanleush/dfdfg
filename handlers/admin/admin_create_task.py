import logging
import re
from aiogram import Router, F, types, Bot, Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.enums import ParseMode
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton
from app.database.crud.tasks import get_active_tasks, get_task_by_id, create_task, delete_task, delete_task_by_id
from app.database.session import AsyncSessionLocal
from app.keyboards.admin import get_admin_main_keyboard
from app.localization.texts import get_texts
from html import escape


logger = logging.getLogger(__name__)
router = Router()


class TaskCreationStates(StatesGroup):
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_channels = State()
    waiting_for_reward = State()


@router.callback_query(F.data == "admin_manage_tasks")
async def admin_manage_tasks(callback: types.CallbackQuery):
    """Отображает меню управления заданиями."""


    async with AsyncSessionLocal() as db:
        tasks = await get_active_tasks(db)

        builder = InlineKeyboardBuilder()
        builder.add(
            InlineKeyboardButton(
                text="➕ Добавить новое задание",
                callback_data="admin_create_task"
            ),
            InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data="admin_panel"
            )
        )

        if tasks:
            for task in tasks:
                builder.add(
                    InlineKeyboardButton(
                        text=f"✏️ {escape(task.title)} ({task.reward_kopeks / 100}₽)",
                        callback_data=f"admin_edit_task_{task.id}"
                    )
                )
                builder.add(
                    InlineKeyboardButton(
                        text="❌ Удалить задание",
                        callback_data=f"admin_delete_task_{task.id}"
                    )
                )

        builder.adjust(1, repeat=True)

        await callback.message.edit_text(
            "Меню управления заданиями:",
            reply_markup=builder.as_markup(),
            parse_mode=ParseMode.HTML
        )
        await callback.answer()


@router.callback_query(F.data == "admin_create_task")
async def start_task_creation(callback: types.CallbackQuery, state: FSMContext):
    """Начинает процесс создания нового задания, запрашивает название."""
    await callback.message.edit_text(
        "📝 <b>Создание задания</b>\n\nВведите <b>название</b> для нового задания:",
        parse_mode=ParseMode.HTML
    )
    await state.set_state(TaskCreationStates.waiting_for_title)
    await callback.answer()

@router.message(TaskCreationStates.waiting_for_title)
async def process_task_title(message: types.Message, state: FSMContext):
    """Принимает название задания и запрашивает описание."""
    await state.update_data(title=message.text.strip())
    await message.answer("✍️ Отлично! Теперь введите <b>описание</b> для задания:", parse_mode=ParseMode.HTML)
    await state.set_state(TaskCreationStates.waiting_for_description)

@router.message(TaskCreationStates.waiting_for_description)
async def process_task_description(message: types.Message, state: FSMContext):
    """Принимает описание задания и запрашивает ID каналов."""
    await state.update_data(description=message.text.strip())
    await message.answer(
        "🔗 Отлично! Теперь отправьте <b>ID каналов</b> и <b>ссылку на них</b>. Формат: <code>ID:ссылка</code>. Разделите каналы запятой, например:\n\n"
        "<code>-1001234567890:https://t.me/+AbcDefGhi, -1009876543210:https://t.me/MyChannel</code>",
        parse_mode=ParseMode.HTML
    )
    await state.set_state(TaskCreationStates.waiting_for_channels)


@router.message(TaskCreationStates.waiting_for_channels)
async def process_task_channels(message: types.Message, state: FSMContext):
    """Принимает ID и ссылки каналов и запрашивает вознаграждение."""
    channels_str = message.text.strip()
    channels_data = []

    # Разбираем каждый канал по ID и ссылке
    for entry in channels_str.split(','):
        entry = entry.strip()
        if ':' not in entry:
            await message.answer("❌ Неверный формат. Пожалуйста, используйте формат <code>ID:ссылка</code>.")
            return

        channel_id_str, channel_url = entry.split(':', 1)

        if not re.match(r"^-?\d+$", channel_id_str):
            await message.answer("❌ Неверный формат ID канала. ID должен быть числом.")
            return

        # Проверка, что ссылка является ссылкой на Telegram
        if not channel_url.startswith(('https://t.me/', 'tg://resolve')):
            await message.answer("❌ Неверный формат ссылки. Пожалуйста, используйте ссылку на Telegram.")
            return

        channels_data.append({
            'id': channel_id_str,
            'url': channel_url,
            'name': channel_id_str  # Добавляем имя канала (используем ID как имя)
        })

    await state.update_data(channels=channels_data)
    await message.answer(
        "💰 Почти готово! Теперь введите <b>вознаграждение</b> в копейках (например, <code>5000</code> для 50 рублей):",
        parse_mode=ParseMode.HTML
    )
    await state.set_state(TaskCreationStates.waiting_for_reward)


@router.message(TaskCreationStates.waiting_for_reward)
async def process_task_reward(message: types.Message, state: FSMContext, db: AsyncSession):
    """Принимает вознаграждение, создает задание и завершает процесс."""
    try:
        reward = int(message.text.strip())
        if reward <= 0:
            await message.answer("❌ Вознаграждение должно быть положительным числом.")
            return

        await state.update_data(reward_kopeks=reward)

        task_data = await state.get_data()

        # Получаем данные о каналах из FSM-состояния
        channels_data = task_data['channels']

        await create_task(
            db,
            title=task_data['title'],
            description=task_data['description'],
            channels=channels_data,
            reward_kopeks=task_data['reward_kopeks']
        )

        await message.answer(
            f"✅ <b>Задание создано!</b>\n\n"
            f"<b>Название:</b> {task_data['title']}\n"
            f"<b>Описание:</b> {task_data['description']}\n"
            f"<b>Вознаграждение:</b> {task_data['reward_kopeks'] / 100}₽",
            parse_mode=ParseMode.HTML
        )
        await state.clear()

    except ValueError:
        await message.answer("❌ Неверный формат. Пожалуйста, введите вознаграждение в копейках (целое число).")
    except Exception as e:
        logger.error(f"Ошибка при создании задания: {e}")
        await message.answer("❌ Произошла ошибка при создании задания. Попробуйте еще раз.")

@router.callback_query(F.data.startswith("admin_delete_task_"))
async def delete_task_callback(callback: types.CallbackQuery, db: AsyncSession):
    try:
        task_id = int(callback.data.split('_')[-1])

        success = await delete_task_by_id(db, task_id)  # Вызываем новую функцию

        if success:
            await callback.message.edit_text("Задание успешно удалено.")
        else:
            await callback.message.edit_text("Ошибка при удалении задания. Возможно, оно уже удалено.")

    except Exception as e:
        logger.error(f"Ошибка при удалении задания: {e}")
        await callback.message.edit_text("Произошла ошибка при удалении задания.")


def register_handlers(dp: Dispatcher):
    """Регистрация обработчиков"""
    dp.include_router(router)
    logger.info("✅ Обработчики админ-панели заданий зарегистрированы")