from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.config import Config

def get_subscription_keyboard() -> InlineKeyboardMarkup:
    """
    Создает клавиатуру с кнопками для подписки на каналы
    """
    buttons = [
        [
            InlineKeyboardButton(
                text="📢 Канал",
                url=f"https://t.me/{Config.CHANNEL_USERNAME}"
            )
        ]
    ]
    
    # Добавляем кнопку группы только если GROUP_USERNAME определен
    if Config.GROUP_USERNAME is not None:
        buttons.append([
            InlineKeyboardButton(
                text="👥 Группа",
                url=f"https://t.me/{Config.GROUP_USERNAME}"
            )
        ])
    
    buttons.append([
        InlineKeyboardButton(
            text="Я подписался",
            callback_data="check_subscription"
        )
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)
