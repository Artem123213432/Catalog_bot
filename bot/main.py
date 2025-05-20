import asyncio
import logging
import os
from datetime import datetime
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from bot.config import Config
from bot.routers import start, catalog, cart, faq
from bot.middlewares.subscription import SubscriptionMiddleware

# Настройка логирования
log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)

log_file = os.path.join(log_dir, f'bot_{datetime.now().strftime("%Y%m%d")}.log')
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
bot = Bot(token=Config.BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

# Регистрация роутеров
dp.include_router(start.router)
dp.include_router(catalog.router)
dp.include_router(cart.router)
dp.include_router(faq.router)

# Регистрация middleware
dp.message.middleware(SubscriptionMiddleware())
dp.callback_query.middleware(SubscriptionMiddleware())

async def main():
    """
    Основная функция запуска бота
    """
    logger.info("Starting bot...")
    # Удаляем вебхук на всякий случай
    await bot.delete_webhook(drop_pending_updates=True)
    
    # Запускаем поллинг
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
