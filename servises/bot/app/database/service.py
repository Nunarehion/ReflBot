from typing import Optional, Dict, Any, List
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo import ASCENDING, DESCENDING
from pathlib import Path
import json

class DatabaseService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.col = self.db.get_collection("messages")

    async def init_indexes(self):
        """Создаёт необходимые индексы при старте."""
        await self.col.create_index("message_id", unique=True)

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

                    # Поддержка двух форматов: legacy collMod и unified {collection, validator, indexes}
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

                        # Создаём индексы
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

    async def get_message(self, message_id: str) -> Optional[Dict[str, Any]]:
        doc = await self.col.find_one({"message_id": message_id}, projection={"_id": False})
        return doc

    async def add_message(self, message_id: str, text: str, media: Optional[str], keyboard: Optional[Dict[str, Any]]):
        doc = {"message_id": message_id, "text": text, "media": media, "keyboard": keyboard}
        await self.col.update_one({"message_id": message_id}, {"$set": doc}, upsert=True)

    async def delete_message(self, message_id: str) -> bool:
        res = await self.col.delete_one({"message_id": message_id})
        return res.deleted_count == 1

    async def update_message(self, message_id: str, **fields):
        if not fields:
            return
        await self.col.update_one({"message_id": message_id}, {"$set": fields})
