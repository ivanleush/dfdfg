# app/services/user_profile_service.py
from app.database.models import User
from app.localization.texts import get_texts
from app.config import settings


class UserProfileService:
    async def get_profile_info(self, user: User) -> str:
        texts = get_texts('ru')

        profile_info = {
            "name": user.full_name or "Не указано",
            "telegram_id": user.telegram_id,
            "balance": f"{user.balance_kopeks / 100:.2f}₽",
            "status": "Активна" if user.status == "active" else "Неактивна",
            "registered_at": user.created_at.strftime("%d.%m.%Y")
        }

        return texts.get_profile_text(**profile_info)