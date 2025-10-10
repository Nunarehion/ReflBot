
from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from app.database.service import DatabaseService
from app.utils.phone import validate_phone_number, normalize_phone_number
from app.event.function.activate import activate_user
import logging

logger = logging.getLogger(__name__)

router = Router()

@router.callback_query(lambda c: c.data == "activate")
async def QueryActivate(callback: types.CallbackQuery, db_service: DatabaseService):
    """Активация пользователя."""
    
    logger.info(f"Activating user with callback data: {callback.data}")
    result = await activate_user(callback, db_service)

    if result:
        await callback.answer("Пользователь успешно активирован!")
    else:
        await callback.answer("Не удалось активировать пользователя.")
