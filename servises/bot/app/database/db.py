from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from env.config_reader import config

async def create_mongo_client() -> AsyncIOMotorClient:
    """Создаёт и возвращает AsyncIOMotorClient."""
    return AsyncIOMotorClient(config.MONGO_URI)

async def get_mongo_db(client: AsyncIOMotorClient | None = None) -> AsyncIOMotorDatabase:
    """Возвращает объект базы данных. Если client не передан — создаёт новый."""
    if client is None:
        client = await create_mongo_client()
    # Если в config есть имя базы как строка:
    db_name = getattr(config, "MONGO_DB_NAME", None) or config.MONGO_URI.rsplit("/", 1)[-1].split("?")[0]
    return client[db_name]
