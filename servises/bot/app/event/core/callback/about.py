# from aiogram import Router, types, F
# from aiogram.filters import Command
# from aiogram.types import Message, CallbackQuery

# from app.event.router import logger
# from app.messages.message import *

# router = Router()

# @router.callback_query(F.data == "query/about")
# async def query_about(callback: CallbackQuery, state: FSMContext):
#     logger.info(f"Получен запрос 'query/about' от пользователя {callback.from_user.id}")
#     await message_about(callback.message)
#     await callback.answer()
#     await state.clear()