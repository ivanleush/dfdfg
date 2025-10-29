from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from typing import List, Optional
from app.database.models import Task, TaskChannel, TaskCompletion
from sqlalchemy.orm import selectinload

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import delete
from app.database.models import Task, TaskCompletion, TaskChannel


async def delete_task_by_id(db: AsyncSession, task_id: int):
    """
    Deletes a task and all related records from the database.
    """
    try:
        # 1. Удаляем все записи о выполнении задания
        await db.execute(delete(TaskCompletion).where(TaskCompletion.task_id == task_id))

        # 2. Удаляем все связанные каналы
        await db.execute(delete(TaskChannel).where(TaskChannel.task_id == task_id))

        # 3. Находим и удаляем само задание
        task = await db.get(Task, task_id)
        if task:
            await db.delete(task)
            await db.commit()
            return True
        else:
            await db.rollback()
            return False

    except Exception as e:
        await db.rollback()
        # Логирование ошибки
        return False


async def create_task(db: AsyncSession, title: str, description: str, channels: List[dict], reward_kopeks: int) -> Task:
    """Создает новое задание с каналами для подписки."""
    new_task = Task(
        title=title,
        description=description,
        reward_kopeks=reward_kopeks,
        is_active=True
    )
    db.add(new_task)
    await db.flush()  # Получаем ID задания перед коммитом

    # Создаем объекты TaskChannel для каждого канала в списке
    for channel_data in channels:
        new_task_channel = TaskChannel(
            task_id=new_task.id,
            name=channel_data['name'],  # Используем 'name' из словаря
            channel_id=channel_data['id'],
            url=channel_data['url']
        )
        db.add(new_task_channel)

    await db.commit()
    await db.refresh(new_task)
    return new_task


async def get_task_by_id(db: AsyncSession, task_id: int) -> Optional[Task]:
    """Получает задание по ID вместе с каналами."""
    result = await db.execute(
        select(Task)
        .where(Task.id == task_id)
        .options(selectinload(Task.channels))  # ✅ Загружаем каналы сразу
    )
    return result.scalars().first()


async def get_active_tasks(db: AsyncSession) -> List[Task]:
    """Возвращает список всех активных заданий."""
    result = await db.execute(
        select(Task).where(Task.is_active == True)
    )
    return result.scalars().all()


async def get_user_completed_tasks(db: AsyncSession, user_id: int) -> List[TaskCompletion]:
    """Возвращает список заданий, выполненных пользователем."""
    result = await db.execute(
        select(TaskCompletion).where(TaskCompletion.user_id == user_id)
    )
    return result.scalars().all()


async def delete_task(db: AsyncSession, task_id: int) -> None:
    """Удаляет задание по ID вместе с каналами."""
    # Сначала находим задание
    result = await db.execute(select(Task).where(Task.id == task_id))
    task = result.scalars().first()

    if task:
        # Удаляем связанные каналы
        await db.execute(delete(TaskChannel).where(TaskChannel.task_id == task_id))
        # Удаляем задание
        await db.delete(task)
        await db.commit()
    else:
        raise ValueError(f"Задание с ID {task_id} не найдено")


async def check_task_completion(db: AsyncSession, user_id: int, task_id: int) -> bool:
    """Проверяет, выполнено ли задание пользователем."""
    result = await db.execute(
        select(TaskCompletion).where(
            TaskCompletion.user_id == user_id,
            TaskCompletion.task_id == task_id
        )
    )
    return result.scalars().first() is not None


async def complete_task(db: AsyncSession, user_id: int, task_id: int) -> TaskCompletion:
    """Отмечает задание как выполненное пользователем."""
    # Проверяем, не выполнено ли уже задание
    is_completed = await check_task_completion(db, user_id, task_id)
    if is_completed:
        raise ValueError("Задание уже выполнено")

    completion = TaskCompletion(
        user_id=user_id,
        task_id=task_id
    )
    db.add(completion)
    await db.commit()
    await db.refresh(completion)
    return completion


async def get_task_with_channels(db: AsyncSession, task_id: int) -> Optional[Task]:
    """Получает задание вместе с его каналами."""
    result = await db.execute(
        select(Task).where(Task.id == task_id)
    )
    task = result.scalars().first()

    if task:
        # Загружаем каналы
        await db.refresh(task, ['channels'])

    return task