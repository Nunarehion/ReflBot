from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from app.messages.message import send_message
from app.database.service import DatabaseService
from app.event.function.activate import activate_user

router = Router()

@router.message(Command("activate"))
async def start_command(message: types.Message, state: FSMContext, db_service: DatabaseService):
    await state.clear()
    result = await activate_user_from_message_by_tg_id(message, db_service)
    if result is None:
        await send_message(message, "activate_not_found")
        return
    await send_message(message, "activate_11")
