from typing import List
from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
import logging

logger = logging.getLogger(__name__)

async def check_subscription(bot: Bot, user_id: int, channels: List[str]) -> bool:
    for channel in channels:
        if not channel:  
            continue
            
        try:
            
            channel_id = f"@{channel}" if not channel.startswith("@") else channel
            logger.info(f"Проверка подписки на канал {channel_id}")
            
            member = await bot.get_chat_member(chat_id=channel_id, user_id=user_id)
            if member.status in ["left", "kicked"]:
                logger.info(f"Пользователь {user_id} не подписан на канал {channel_id}")
                return False
                
            logger.info(f"Пользователь {user_id} подписан на канал {channel_id}")
            return True
            
        except TelegramBadRequest as e:
            logger.error(f"Ошибка при проверке подписки на канал {channel_id}: {e}")
            return False
            
    return False
