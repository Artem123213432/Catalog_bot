import logging
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from bot.config import Config
from bot.utils.subscription import check_subscription

logger = logging.getLogger(__name__)

class SubscriptionMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        # Пропускаем проверку, если канал не настроен
        if not Config.CHANNEL_USERNAME:
            logger.info("Канал не настроен, пропускаем проверку подписки.")
            return await handler(event, data)

        # Пропускаем проверку для администраторов
        if hasattr(Config, 'ADMIN_IDS') and event.from_user.id in Config.ADMIN_IDS:
            logger.info(f"Пользователь {event.from_user.id} является администратором, пропускаем проверку подписки.")
            return await handler(event, data)

        # Проверяем подписку только на канал (группа не обязательна)
        channels = [Config.CHANNEL_USERNAME]
        bot = data["bot"]
        is_subscribed = await check_subscription(
            bot=bot,
            user_id=event.from_user.id,
            channels=channels
        )

        if not is_subscribed:
            logger.info(f"Пользователь {event.from_user.id} не подписан на канал {Config.CHANNEL_USERNAME}.")
            from bot.keyboards.inline import get_subscription_keyboard
            if isinstance(event, CallbackQuery):
                await event.answer(
                    "Для использования бота необходимо подписаться на канал!",
                    show_alert=True
                )
                return
            await event.answer(
                "Для использования бота необходимо подписаться на канал!",
                reply_markup=get_subscription_keyboard()
            )
            return

        logger.info(f"Пользователь {event.from_user.id} подписан на канал {Config.CHANNEL_USERNAME}.")
        return await handler(event, data)
