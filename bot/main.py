import asyncio
import logging
import os
import sys
from datetime import datetime
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from dotenv import load_dotenv


load_dotenv()


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)
sys.path.append(os.path.join(BASE_DIR, 'admin_panel'))


log_dir = os.path.join(BASE_DIR, 'logs')
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


sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))


logger.info("Настройка Django ORM...")
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'admin_panel.settings')
django.setup()
logger.info("Django ORM настроен успешно")


from config import Config
from routers import start, catalog, cart, faq
from middlewares.subscription import SubscriptionMiddleware


try:
    from utils.mailer import check_and_send_mailings
    logger.info("Импорт check_and_send_mailings прошёл успешно.")
except Exception as e:
    logger.error(f"Ошибка при импорте check_and_send_mailings: {e}", exc_info=True)
    check_and_send_mailings = None


logger.info(f"Инициализация бота с токеном: {Config.BOT_TOKEN[:5]}...")
bot = Bot(token=Config.BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()


dp.include_router(start.router)
dp.include_router(catalog.router)
dp.include_router(cart.router)
dp.include_router(faq.router)


dp.message.middleware(SubscriptionMiddleware())
dp.callback_query.middleware(SubscriptionMiddleware())

async def main():
    logger.info("Starting bot...")
    
    await bot.delete_webhook(drop_pending_updates=True)
    
    
    try:
        if check_and_send_mailings:
            logger.info("Запуск фоновой задачи для проверки и отправки рассылок...")
            background_task = asyncio.create_task(check_and_send_mailings(bot))
            logger.info("Фоновая задача рассылки запущена успешно.")
        else:
            logger.error("Фоновая задача рассылки не запущена из-за ошибки импорта!")
    except Exception as e:
        logger.error(f"Ошибка при запуске фоновой задачи рассылки: {e}", exc_info=True)
    
    
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
