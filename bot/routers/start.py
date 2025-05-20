from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from bot.keyboards.inline import get_subscription_keyboard
from bot.utils.subscription import check_subscription
from bot.config import Config
import logging

logger = logging.getLogger(__name__)
router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    """
    Обработчик команды /start
    """
    await message.answer(
        f"Привет, {message.from_user.full_name}! Я бот магазина.\n\n"
        "Доступные команды:\n"
        "/catalog - Просмотр каталога товаров\n"
        "/cart - Просмотр корзины\n"
        "/faq - Часто задаваемые вопросы"
    )

@router.callback_query(F.data == "check_subscription")
async def check_subscription_callback(callback: CallbackQuery):
    """
    Обработчик нажатия на кнопку "Я подписался"
    """
    try:
        logger.info(f"Проверка подписки для пользователя {callback.from_user.id}")
        
        # Сначала отвечаем на callback, чтобы убрать часики
        await callback.answer()
        
        is_subscribed = await check_subscription(
            bot=callback.bot,
            user_id=callback.from_user.id,
            channels=[Config.CHANNEL_USERNAME]
        )
        
        logger.info(f"Результат проверки подписки: {is_subscribed}")

        if is_subscribed:
            logger.info(f"Пользователь {callback.from_user.id} подписан, отправляем приветствие")
            await callback.message.edit_text(
                f"Привет, {callback.from_user.full_name}! Я бот магазина.\n\n"
                "Доступные команды:\n"
                "/catalog - Просмотр каталога товаров\n"
                "/cart - Просмотр корзины\n"
                "/faq - Часто задаваемые вопросы"
            )
        else:
            logger.info(f"Пользователь {callback.from_user.id} не подписан")
            await callback.message.edit_text(
                "Для использования бота необходимо подписаться на канал!",
                reply_markup=get_subscription_keyboard()
            )
            
    except Exception as e:
        logger.error(f"Ошибка при проверке подписки: {e}", exc_info=True)
        await callback.answer(
            "Произошла ошибка при проверке подписки. Попробуйте позже.",
            show_alert=True
        )
