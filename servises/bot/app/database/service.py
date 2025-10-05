from typing import Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase

class DatabaseService:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.col = self.db.get_collection("messages")

    async def init_indexes(self):
        """Создаёт необходимые индексы при старте."""
        await self.col.create_index("message_id", unique=True)

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
