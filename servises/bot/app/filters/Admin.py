# app/filters.py
from aiogram.filters import BaseFilter
from aiogram.types import Message

class DBAdminFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        if not message.from_user:
            return False
 
        dispatcher = message.get_bot().dispatcher
        db_service = dispatcher.get('db_service')
        if not db_service:
            return False
        user = await db_service.get_user_by_id(message.from_user.id)
        return bool(user and user.get("is_admin"))
