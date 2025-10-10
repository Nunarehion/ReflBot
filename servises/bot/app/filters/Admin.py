from aiogram.filters import BaseFilter
from aiogram.types import Message
from typing import Optional


class DBAdminFilter(BaseFilter):
    def __init__(self, db_service: DatabaseService):
        self.db_service = db_service

    async def __call__(self, message: Message) -> bool:
        if not message.from_user:
            return False

        user = await self.db_service.get_user_by_telegram_id(message.from_user.id)
        return bool(user and user.get("is_admin"))