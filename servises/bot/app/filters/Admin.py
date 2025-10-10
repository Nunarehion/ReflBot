from aiogram.filters import BaseFilter
from aiogram.types import Message

class DBAdminFilter(BaseFilter):
    def __init__(self, required_access: str | None = None):
        self.required_access = required_access

    async def __call__(self, message: Message) -> bool:
        if not message.from_user:
            return False

        dispatcher = getattr(message.bot, "dispatcher", None)
        if not dispatcher:
           return False

        db_service = dispatcher.get("db_service")
        if not db_service:
            return False
            
        admin = await db_service.get_admin_by_telegram_id(message.from_user.id)
        if not admin:
            return False

        if self.required_access and admin.get("access_level") != self.required_access:
            return False

        return True
