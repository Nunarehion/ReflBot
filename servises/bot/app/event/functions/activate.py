from typing import Optional, Dict, Any
from aiogram import types
from app.database.service import DatabaseService
from app.utils.phone import validate_phone_number, normalize_phone_number

def _tg_id_from_arg(arg: str, db_service: DatabaseService) -> Optional[int]:
    if arg.isdigit():
        return int(arg)
    if validate_phone_number(arg):
        phone = normalize_phone_number(arg)
        user = db_service.get_user_by_phone(phone)  # sync call assumed; wrapped below for async
        return user.get("telegram_id") or user.get("id") if user else None
    username = arg.lstrip("@")
    user = db_service.get_user_by_username(username)
    return user.get("telegram_id") or user.get("id") if user else None

async def activate_user(
    message: types.Message,
    db_service: DatabaseService,
) -> Optional[Dict[str, Any]]:
    tg_id: Optional[int] = None

    if message.forward_from:
        txt = (message.text or message.caption or "").strip()
        if txt.split(maxsplit=1)[0].startswith("/activate") and getattr(message.forward_from, "id", None):
            tg_id = message.forward_from.id

    if tg_id is None:
        args = message.get_args().strip()
        if not args:
            return None
        arg0 = args.split()[0]

        if arg0.isdigit():
            tg_id = int(arg0)
        elif validate_phone_number(arg0):
            phone = normalize_phone_number(arg0)
            user = await db_service.get_user_by_phone(phone)
            tg_id = user.get("telegram_id") or user.get("id") if user else None
        else:
            username = arg0.lstrip("@")
            user = await db_service.get_user_by_username(username)
            tg_id = user.get("telegram_id") or user.get("id") if user else None

        if not tg_id:
            return None

    return await db_service.activate_user(telegram_id=tg_id)