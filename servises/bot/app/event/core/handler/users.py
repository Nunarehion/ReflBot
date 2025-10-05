import asyncio
from aiogram import Router, types
from aiogram.filters import Command
from app.event.router import logger
from app.database.service import DatabaseService
from app.messages.message import send_message

router = Router()

@router.message(Command("users"))
async def get_users_command(message: types.Message, db_service: DatabaseService):
    logger.info(f"Получена команда /users от пользователя {message.from_user.id}")
    
    all_users = await db_service.get_all_users()
    
    if not all_users:
        await message.answer("В базе данных нет зарегистрированных пользователей.")
        return
        
    user_list_items = []
    for user in all_users:
        username = f"@{user.username}" if user.username else "Нет username"
        full_name = user.full_name if user.full_name else "Нет имени"
        premium_status = "⭐ Premium" if user.is_premium else ""
        user_list_items.append(
            f"ID: {user.user_id}\nИмя: {full_name}\nUsername: {username} {premium_status}"
        )
    
    user_list_text = "\n\n".join(user_list_items)
    await send_message(message, "user_list", db_service=db_service, user_list_text=user_list_text)
