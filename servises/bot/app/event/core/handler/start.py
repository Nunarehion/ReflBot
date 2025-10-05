# servises/bot/app/event/core/handler/start.py

from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from app.messages.message import send_message

router = Router()

@router.message(Command("start"))
async def start_command(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("start")
    await send_message(message, "welcome_001")