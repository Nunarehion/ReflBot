from typing import Optional, Any, Dict, List
from aiogram import types
from aiogram.exceptions import TelegramAPIError
from app.database.service import DatabaseService
from app.database.db import create_mongo_client, get_mongo_db
import json

import logging

def _build_inline_keyboard(reply_markup: Optional[Dict[str, Any]]) -> Optional[types.InlineKeyboardMarkup]:
    logging.info("%s", reply_markup)
    if not reply_markup or not isinstance(reply_markup, dict):
        logging.info("reply_markup is None or not dict")
        return None

    rows = reply_markup.get("inline_keyboard")
    if not rows or not isinstance(rows, list):
        logging.info("inline_keyboard missing or not a list")
        return None

    try:
        serialized_rows: List[List[Dict[str, Any]]] = []
        for row in rows:
            if not isinstance(row, list):
                continue
            serialized_row: List[Dict[str, Any]] = []
            for btn in row:
                if not isinstance(btn, dict):
                    continue
                text = str(btn.get("text", ""))
                cb = btn.get("callback_data")
                url = btn.get("url")
                btn_payload: Dict[str, Any] = {"text": text}
                if cb is not None:
                    btn_payload["callback_data"] = str(cb)
                elif url is not None:
                    btn_payload["url"] = str(url)
                serialized_row.append(btn_payload)
            if serialized_row:
                serialized_rows.append(serialized_row)

        if not serialized_rows:
            logging.info("no valid buttons found")
            return None

        kb_dict = {"inline_keyboard": serialized_rows}
        try:
            if hasattr(types.InlineKeyboardMarkup, "model_validate"):
                kb = types.InlineKeyboardMarkup.model_validate(kb_dict)
            else:
                kb = types.InlineKeyboardMarkup(**kb_dict)
        except Exception:
            if hasattr(types.InlineKeyboardMarkup, "model_construct"):
                kb = types.InlineKeyboardMarkup.model_construct()
                setattr(kb, "inline_keyboard", serialized_rows)
            else:
                logging.exception("failed to construct InlineKeyboardMarkup")
                return None

        if not getattr(kb, "inline_keyboard", None):
            logging.info("kb.inline_keyboard empty after construct")
            return None

        return kb

    except Exception:
        logging.exception("Error building inline keyboard")
        return None


   


async def send_message(
    chat: types.Message | types.CallbackQuery,
    message_id: str,
    **kwargs
) -> Optional[types.Message]:
    bot = chat.bot

    db_service: DatabaseService = getattr(bot, "db_service", None)
    
    if db_service is None:
        chat.answer(f"db_service None {db_service}")
        client = await create_mongo_client()
        db = await get_mongo_db(client)
        db_service = DatabaseService(db)
        if hasattr(db_service, "init_indexes"):
            await db_service.init_indexes()
        bot.db_service = db_service
        bot.mongo_client = client

    try:
        message_doc = await db_service.get_message(message_id)
        if not message_doc:
            try:
                await chat.answer(f"message None {message_id}")
            except Exception:
                pass
            return None

        text: str = message_doc.get("text", "")
        try:
            formatted_text = text.format(**kwargs) if kwargs else text
        except Exception:
            formatted_text = text

        reply_markup_raw = message_doc.get("reply_markup")
        if isinstance(reply_markup_raw, str):
            try:
                reply_markup = json.loads(reply_markup_raw)
            except Exception:
                reply_markup = None
        else:
            reply_markup = reply_markup_raw

        keyboard = _build_inline_keyboard(reply_markup) if reply_markup else None

        parse_mode = message_doc.get("parse_mode")
        disable_preview = message_doc.get("disable_web_page_preview", False)

        if isinstance(chat, types.Message):
            return await chat.answer(
                formatted_text,
                reply_markup=keyboard,
                parse_mode=parse_mode,
                disable_web_page_preview=disable_preview
            )

        if isinstance(chat, types.CallbackQuery):
            return await chat.message.answer(
                formatted_text,
                reply_markup=keyboard,
                parse_mode=parse_mode,
                disable_web_page_preview=disable_preview
            )

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
