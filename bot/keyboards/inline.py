from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.config import Config

def get_subscription_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [
            InlineKeyboardButton(
                text="📢 Канал",
                url=f"https://t.me/{Config.CHANNEL_USERNAME}"
            )
        ]
    ]
    
    
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

def get_welcome_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(text="📦 Каталог товаров", callback_data="show_catalog"),
        ],
        [
            InlineKeyboardButton(text="🛒 Корзина", callback_data="show_cart"),
        ],
        [
            InlineKeyboardButton(text="❓ FAQ", callback_data="show_faq"),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
