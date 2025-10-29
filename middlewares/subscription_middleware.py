from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware, types
from aiogram.enums import ChatMemberStatus
from app.config import settings
from app.database.crud.user import get_user_by_telegram_id
from app.database.models import UserStatus
from app.localization.texts import get_texts
from app.keyboards.inline import get_subscription_keyboard


class SubscriptionMiddleware(BaseMiddleware):
    async def __call__(
            self,
            handler: Callable[[types.Message, Dict[str, Any]], Awaitable[Any]],
            event: types.Message,
            data: Dict[str, Any]
    ) -> Any:
        user_id = event.from_user.id
        db = data.get('db')
        bot = data.get('bot')

        is_subscribed = await check_channel_subscription(bot, user_id)

        if not is_subscribed:
            # Отправка сообщения с просьбой подписаться
            language = 'ru'
            texts = get_texts(language)
            subscription_text = texts.SUBSCRIPTION_REQUIRED
            for channel in settings.SUBSCRIPTION_CHANNELS:
                subscription_text += f"\n👉 {channel['name']}: {channel['url']}"
            subscription_text += texts.SUBSCRIPTION_AFTER
            await event.answer(
                subscription_text,
                reply_markup=get_subscription_keyboard(texts),
                disable_web_page_preview=True
            )
            return  # Прерывание выполнения команды

        return await handler(event, data)


async def check_channel_subscription(bot, user_id):
    # Логика из вашего файла
    for channel_id in settings.SUBSCRIPTION_CHANNEL_IDS:
        member = await bot.get_chat_member(
            chat_id=channel_id,
            user_id=user_id
        )
        if member.status not in [
            ChatMemberStatus.MEMBER,
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.CREATOR
        ]:
            return False
    return True