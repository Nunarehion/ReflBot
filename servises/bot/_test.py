import asyncio
import logging
from aiogram import Bot, Dispatcher, types, Router
from aiogram.filters import CommandStart
from env.config_reader import config

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)

router = Router()

@router.message(CommandStart())
async def cmd_start(message: types.Message):
    await message.answer("Привет! Я тестовый бот.")

async def main():
    bot = Bot(token=config.TELEGRAM_BOT_TOKEN.get_secret_value())
    dp = Dispatcher()
    dp.include_router(router)
    
    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("Бот запущен. Начинаю опрос...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())