# servises/bot/app/event/core/handler/start.py

from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from app.messages.message import send_message
from app.database.service import DatabaseService

router = Router()

@router.message(Command("start"))
async def start_command(message: types.Message, state: FSMContext, db_service: DatabaseService):
    """Обработчик команды /start."""
    await state.clear()
    user = await db_service.get_user_by_telegram_id(message.from_user.id)
    
    if user:
        # Пользователь уже зарегистрирован
        await message.answer(
            f"Добро пожаловать обратно!\n"
            f"Ваш реферальный код: {user['referral_code']}\n"
            f"Баланс: {user['points']} баллов\n"
            f"Статус: {'Активирован' if user['is_activated'] else 'Ожидает активации'}"
        )
        return
    await send_message(message, "welcome_v1")