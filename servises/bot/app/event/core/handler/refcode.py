from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from app.database.service import DatabaseService
from app.fsm.registration import RegistrationStates
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

router = Router()

@router.message(Command("refcode"))
async def add_referral_code_later(message: types.Message, state: FSMContext, db_service: DatabaseService):
    """Позволяет ввести реферальный код после регистрации (в течение 48 часов)."""
    user = await db_service.get_user_by_telegram_id(message.from_user.id)
    
    if not user:
        await message.answer("❌ Вы не зарегистрированы. Используйте /start для регистрации.")
        return
    
    if user.get("referrer_id"):
        await message.answer("❌ У вас уже есть реферер.")
        return
    
    # Проверяем дедлайн 48 часов
    if user.get("refcode_deadline") and datetime.now() > user["refcode_deadline"]:
        await message.answer("❌ Время для ввода реферального кода истекло (48 часов).")
        return
    
    await state.set_state(RegistrationStates.waiting_for_referral_code)
    await message.answer(
        "🎁 Введите реферальный код для получения 100 баллов:\n\n"
        "⏰ Осталось времени: до истечения 48 часов с регистрации"
    )
