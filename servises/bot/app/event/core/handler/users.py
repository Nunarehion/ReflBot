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
        username = f"@{user.get('username')}" if user.get('username') else "Нет username"
        full_name = user.get('full_name') or "Нет имени"
        premium_status = "⭐ Premium" if user.get('is_premium') else ""
        user_list_items.append(
            "ID: {id}\nИмя: {name}\nUsername: {username} {premium}".format(
                id=user.get('user_id'),
                name=full_name,
                username=username,
                premium=premium_status
            )
        )
    
    user_list_text = "\n\n".join(user_list_items)
    await message.answer(user_list_text)

