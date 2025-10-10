from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from app.messages.message import send_message
from app.database.service import DatabaseService

router = Router()

@router.message(Command("activate"))
async def start_command(message: types.Message, state: FSMContext, db_service: DatabaseService):
 ...