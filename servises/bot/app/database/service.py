from typing import Optional, Dict, Any, List
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ASCENDING, DESCENDING
from pathlib import Path
import json
import logging
from datetime import datetime, timedelta
import random
import string

class DatabaseService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.col_messages = self.db.get_collection("messages")
        self.col_users = self.db.get_collection("users")
        self.col_referrals = self.db.get_collection("referrals")
        self.col_admins = self.db.get_collection("admins")
        self.col_point_transactions = self.db.get_collection("point_transactions")


    async def init_indexes(self):
        """Создаёт необходимые индексы при старте."""
        await self.col_messages.create_index("message_id", unique=True)

    async def _ensure_collection(self, name: str) -> None:
        collections: List[str] = await self.db.list_collection_names()
        if name not in collections:
            await self.db.create_collection(name)

    async def init_business_schemas_and_indexes(self) -> None:
        """Применяет JSON-схемы (collMod) и создаёт индексы для бизнес-коллекций."""
        base_dir = Path(__file__).resolve().parent
        schemas_dir = base_dir / "schemas"
        has_schema_files = False
        if schemas_dir.exists():
            for schema_file in schemas_dir.glob("*.json"):
                has_schema_files = True
                try:
                    with schema_file.open("r", encoding="utf-8") as f:
                        spec = json.load(f)
                    if "collMod" in spec:
                        coll_name = spec.get("collMod")
                        if coll_name:
                            await self._ensure_collection(coll_name)
                            await self.db.command(spec)
                    else:
                        collection = spec.get("collection")
                        if not collection:
                            continue
                        await self._ensure_collection(collection)

                        validator = spec.get("validator")
                        validation_level = spec.get("validationLevel", "moderate")
                        if validator:
                            await self.db.command({
                                "collMod": collection,
                                "validator": validator,
                                "validationLevel": validation_level
                            })

                        # Индексы
                        indexes = spec.get("indexes", [])
                        coll = self.db.get_collection(collection)
                        for index in indexes:
                            keys = index.get("keys")
                            options = index.get("options", {})
                            if not keys:
                                continue
                            key_list = []
                            for field, order in keys:
                                key_list.append((field, ASCENDING if order >= 0 else DESCENDING))
                            await coll.create_index(
                                key_list,
                                name=options.get("name"),
                                unique=options.get("unique", False),
                                sparse=options.get("sparse")
                            )
                except Exception:
                    pass
    
    #-------MESAGE-------#
    async def get_message(self, message_id: str) -> Optional[Dict[str, Any]]:
        doc = await self.col_messages.find_one({"message_id": message_id}, projection={"_id": False})
        return doc

    async def add_message(self, message_id: str, text: str, media: Optional[str], keyboard: Optional[Dict[str, Any]]):
        doc = {"message_id": message_id, "text": text, "media": media, "keyboard": keyboard}
        await self.col_messages.update_one({"message_id": message_id}, {"$set": doc}, upsert=True)

    async def delete_message(self, message_id: str) -> bool:
        res = await self.col_messages.delete_one({"message_id": message_id})
        return res.deleted_count == 1

    async def update_message(self, message_id: str, **fields):
        if not fields:
            return
        await self.col_messages.update_one({"message_id": message_id}, {"$set": fields})
    
    #-------USER-------#
    async def generate_referral_code(self) -> str:
        """Генерирует уникальный реферальный код."""
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            existing = await self.col_users.find_one({"referral_code": code})
            if not existing:
                return code

    async def add_user(self, telegram_id: int, phone_number: str, username: Optional[str] = None, full_name: Optional[str] = None) -> Dict[str, Any]:
        """Создаёт нового пользователя."""
        referral_code = await self.generate_referral_code()
        now = datetime.now()
        refcode_deadline = now + timedelta(hours=48)
        
        doc = {
            "telegram_id": telegram_id,
            "phone_number": phone_number,
            "username": username,
            "full_name": full_name,
            "referral_code": referral_code,
            "referrer_id": None,
            "points": 0,
            "is_activated": False,
            "registration_date": now,
            "refcode_deadline": refcode_deadline
        }
        
        result = await self.col_users.insert_one(doc)
        doc["_id"] = result.inserted_id
        return doc

    async def get_user_by_telegram_id(self, telegram_id: int) -> Optional[Dict[str, Any]]:
        """Получает пользователя по telegram_id."""
        return await self.col_users.find_one({"telegram_id": telegram_id}, projection={"_id": False})

    async def get_user_by_phone(self, phone_number: str) -> Optional[Dict[str, Any]]:
        """Получает пользователя по номеру телефона."""
        return await self.col_users.find_one({"phone_number": phone_number}, projection={"_id": False})

    async def get_user_by_referral_code(self, referral_code: str) -> Optional[Dict[str, Any]]:
        """Получает пользователя по реферальному коду."""
        return await self.col_users.find_one({"referral_code": referral_code}, projection={"_id": False})

    async def process_referral_code(self, new_user_telegram_id: int, referral_code: str) -> Dict[str, Any]:
        """
        Обрабатывает ввод реферального кода новым пользователем.
        Возвращает результат операции и данные для уведомлений.
        """
        # Проверяем, что пользователь существует и не имеет реферера
        new_user = await self.get_user_by_telegram_id(new_user_telegram_id)
        if not new_user:
            return {"success": False, "error": "Пользователь не найден"}
        
        if new_user.get("referrer_id"):
            return {"success": False, "error": "У вас уже есть реферер"}
        
        # Проверяем дедлайн 48 часов
        if new_user.get("refcode_deadline") and datetime.now() > new_user["refcode_deadline"]:
            return {"success": False, "error": "Время для ввода реферального кода истекло"}
        
        # Проверяем, что код не свой
        if new_user.get("referral_code") == referral_code:
            return {"success": False, "error": "Нельзя использовать свой реферальный код"}
        
        # Ищем владельца реферального кода
        referrer = await self.get_user_by_referral_code(referral_code)
        if not referrer:
            return {"success": False, "error": "Реферальный код не найден"}
        
        # Устанавливаем связь реферала
        success = await self.update_user_referrer(new_user_telegram_id, referrer["telegram_id"])
        if not success:
            return {"success": False, "error": "Не удалось установить связь с реферером"}
        
        # Создаём запись в таблице рефералов
        await self.add_referral(referrer["telegram_id"], new_user_telegram_id)
        
        # Начисляем баллы: +100 новому пользователю, +25 рефереру
        await self.add_points(
            new_user_telegram_id, 
            100, 
            "использование реферального кода",
            {"referrer_id": referrer["telegram_id"], "referred_user_id": new_user_telegram_id},
            bot
        )
        
        await self.add_points(
            referrer["telegram_id"], 
            25, 
            "использование реферального кода",
            {"referrer_id": referrer["telegram_id"], "referred_user_id": new_user_telegram_id},
            bot
        )
        
        return {
            "success": True,
            "new_user_points": 100,
            "referrer_points": 25,
            "referrer_telegram_id": referrer["telegram_id"],
            "referrer_username": referrer.get("username"),
            "referrer_full_name": referrer.get("full_name")
        }

    async def activate_user(self, telegram_id: int) -> Dict[str, Any]:
        """
        Активирует пользователя и начисляет +75 баллов рефереру.
        Возвращает результат операции и данные для уведомлений.
        """
        user = await self.get_user_by_telegram_id(telegram_id)
        if not user:
            return {"success": False, "error": "Пользователь не найден"}
        
        if user.get("is_activated"):
            return {"success": False, "error": "Пользователь уже активирован"}
        
        # Активируем пользователя
        result = await self.col_users.update_one(
            {"telegram_id": telegram_id},
            {"$set": {"is_activated": True}}
        )
        
        if result.modified_count == 0:
            return {"success": False, "error": "Не удалось активировать пользователя"}
        
        # Активируем реферала в таблице referrals
        await self.activate_referral(telegram_id)
        
        # Если есть реферер, начисляем ему +75 баллов
        referrer_data = None
        if user.get("referrer_id"):
            await self.add_points(
                user["referrer_id"], 
                75, 
                "активация реферала",
                {"referrer_id": user["referrer_id"], "referred_user_id": telegram_id}
            )
            
            # Получаем данные реферера для уведомления
            referrer = await self.get_user_by_telegram_id(user["referrer_id"])
            if referrer:
                referrer_data = {
                    "telegram_id": referrer["telegram_id"],
                    "username": referrer.get("username"),
                    "full_name": referrer.get("full_name"),
                    "points": 75
                }
        
        return {
            "success": True,
            "activated_user": {
                "telegram_id": telegram_id,
                "username": user.get("username"),
                "full_name": user.get("full_name")
            },
            "referrer": referrer_data
        }

    async def add_points(self, telegram_id: int, amount: int, reason: str, ref_data: Optional[Dict] = None) -> bool:
        """Добавляет баллы пользователю."""
        # Получаем текущий баланс
        user = await self.get_user_by_telegram_id(telegram_id)
        if not user:
            return False
            
        # Обновляем баланс
        result = await self.col_users.update_one(
            {"telegram_id": telegram_id},
            {"$inc": {"points": amount}}
        )
        
        if result.modified_count > 0:
            # Записываем транзакцию
            await self.add_point_transaction(telegram_id, amount, "начисление", reason, ref_data)
            return True
        return False

    async def subtract_points(self, telegram_id: int, amount: int, reason: str) -> bool:
        """Списывает баллы с пользователя."""
        # Проверяем, что у пользователя достаточно баллов
        user = await self.get_user_by_telegram_id(telegram_id)
        if not user or user["points"] < amount:
            return False
            
        # Обновляем баланс
        result = await self.col_users.update_one(
            {"telegram_id": telegram_id},
            {"$inc": {"points": -amount}}
        )
        
        if result.modified_count > 0:
            # Записываем транзакцию
            await self.add_point_transaction(telegram_id, -amount, "списание", reason)
            return True
        return False

    async def zero_points(self, telegram_id: int, reason: str) -> bool:
        """Обнуляет баллы пользователя."""
        user = await self.get_user_by_telegram_id(telegram_id)
        if not user or user["points"] == 0:
            return False
            
        current_points = user["points"]
        
        # Обнуляем баланс
        result = await self.col_users.update_one(
            {"telegram_id": telegram_id},
            {"$set": {"points": 0}}
        )
        
        if result.modified_count > 0:
            # Записываем транзакцию
            await self.add_point_transaction(telegram_id, -current_points, "обнуление", reason)
            return True
        return False

    async def get_user_referrals(self, telegram_id: int) -> List[Dict[str, Any]]:
        """Получает список рефералов пользователя."""
        referrals = await self.col_referrals.find(
            {"referrer_id": telegram_id},
            projection={"_id": False}
        ).to_list(length=None)
        return referrals

    async def get_all_users(self) -> List[Dict[str, Any]]:
        """Получает всех пользователей."""
        users = await self.col_users.find(projection={"_id": False}).to_list(length=None)
        return users

    #-------REFERRALS-------#
    async def add_referral(self, referrer_id: int, referred_user_id: int) -> bool:
        """Создаёт связь реферала."""
        doc = {
            "referrer_id": referrer_id,
            "referred_user_id": referred_user_id,
            "status": "pending",
            "created_at": datetime.now(),
            "activated_at": None
        }
        
        try:
            await self.col_referrals.insert_one(doc)
            return True
        except Exception:
            return False

    async def activate_referral(self, referred_user_id: int) -> bool:
        """Активирует реферала."""
        result = await self.col_referrals.update_one(
            {"referred_user_id": referred_user_id, "status": "pending"},
            {"$set": {"status": "activated", "activated_at": datetime.now()}}
        )
        return result.modified_count > 0

    #-------POINT_TRANSACTIONS-------#
    async def add_point_transaction(self, user_id: int, amount: int, transaction_type: str, reason: str, ref_data: Optional[Dict] = None):
        """Добавляет запись о транзакции баллов."""
        doc = {
            "user_id": user_id,
            "amount": amount,
            "transaction_type": transaction_type,
            "reason": reason,
            "ref": ref_data,
            "timestamp": datetime.now()
        }
        await self.col_point_transactions.insert_one(doc)

    #-------ADMINS-------#
    async def is_admin(self, telegram_id: int) -> bool:
        """Проверяет, является ли пользователь администратором."""
        admin = await self.col_admins.find_one({"telegram_id": telegram_id})
        return admin is not None

    async def add_admin(self, telegram_id: int, username: Optional[str] = None, access_level: str = "full") -> bool:
        """Добавляет администратора."""
        doc = {
            "telegram_id": telegram_id,
            "username": username,
            "access_level": access_level
        }
        
        try:
            await self.col_admins.insert_one(doc)
            return True
        except Exception:
            return False
        
