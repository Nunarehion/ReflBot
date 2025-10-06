import asyncio
import logging
from aiogram import Bot, Dispatcher
from app.event.router import router
from app.database.db import create_mongo_client, get_mongo_db
from app.database.service import DatabaseService
from env.config_reader import config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def on_startup(dispatcher: Dispatcher):
    logging.info("Entering on_startup function...")
    try:
        client = await create_mongo_client()
        db = await get_mongo_db(client)
        db_service = DatabaseService(db)
        # Инициализация валидаторов и индексов (идемпотентно)
        try:
            await db_service.init_business_schemas_and_indexes()
        except Exception as e:
            logging.warning(f"Business schema/index init warning: {e}")
        dispatcher['mongo_client'] = client
        dispatcher['db_service'] = db_service
        logging.info("Mongo client and DatabaseService created successfully.")
    except Exception as e:
        logging.error(f"Failed to initialize database services: {e}")
        # Останавливаем polling — Dispatcher.stop_polling асинхронен в aiogram 3.x
        await dispatcher.stop_polling()
        logging.info("Polling stopped due to DB connection failure.")

async def on_shutdown(dispatcher: Dispatcher):
    logging.info("Entering on_shutdown function...")
    client = dispatcher.get('mongo_client')
    if client:
        client.close()
        logging.info("Mongo client closed successfully.")
    else:
        logging.warning("Mongo client was not found in dispatcher context.")

async def main():
    bot = Bot(token=config.TELEGRAM_BOT_TOKEN.get_secret_value())
    dp = Dispatcher()
    dp.include_router(router)
    logging.info("Router included in Dispatcher.")

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    logging.info("Бот запущен. Начинаю опрос...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
