from typing import Optional
from aiogram import types
from aiogram.exceptions import TelegramAPIError
from app.database.service import DatabaseService
from app.database.db import create_mongo_client, get_mongo_db

async def send_message(
    chat: types.Message | types.CallbackQuery,
    message_id: str,
    **kwargs
) -> Optional[types.Message]:
    chat.answer("send")
    bot = chat.bot

    db_service = getattr(bot, "db_service", None)
    if db_service is None:
        chat.answer("db_service NONE")
        client = await create_mongo_client()
        db = await get_mongo_db(client)
        db_service = DatabaseService(db)

        if hasattr(db_service, "init_indexes"):
            await db_service.init_indexes()
        bot.db_service = db_service
        bot.mongo_client = client  # чтобы позже закрыть
    try:
        chat.answer("TRY")
        message = await db_service.get_message(message_id)
        if not message:
            chat.answer(f"message None {message}, {message_id}")
            return None

        text = message.get("text", "")
        formatted_text = text.format(**kwargs)

        if isinstance(chat, types.Message):
            return await chat.answer(formatted_text)

        if isinstance(chat, types.CallbackQuery):
            return await chat.message.answer(formatted_text)

    except TelegramAPIError as e:
        try:
            await chat.answer(f"TelegramAPIError: {e}")
        except Exception:
            pass
    except Exception as e:
        try:
            await chat.answer(f"General Error: {e}")
        except Exception:
            pass

    return None
