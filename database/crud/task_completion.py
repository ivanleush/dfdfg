from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime
from app.database.models import TaskCompletion, Task, User


async def create_task_completion(db: AsyncSession, user_id: int, task_id: int):
    """
    Creates a new task completion record in the database.
    """
    new_completion = TaskCompletion(
        user_id=user_id,
        task_id=task_id,
        completed_at=datetime.utcnow()
    )
    db.add(new_completion)
    await db.commit()
    await db.refresh(new_completion)
    return new_completion


async def check_task_completion(db: AsyncSession, user_id: int, task_id: int) -> bool:
    """
    Checks if a user has already completed a specific task.
    """
    result = await db.execute(
        select(TaskCompletion)
        .where(TaskCompletion.user_id == user_id)
        .where(TaskCompletion.task_id == task_id)
    )
    completion = result.scalar_one_or_none()
    return completion is not None