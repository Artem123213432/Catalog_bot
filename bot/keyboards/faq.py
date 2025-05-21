from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Dict
from bot.data.faq import FAQ_DATA

def get_faq_keyboard() -> InlineKeyboardMarkup:
    keyboard = []
    for i, item in enumerate(FAQ_DATA):
        keyboard.append([
            InlineKeyboardButton(
                text=f"❓ {item['question']}",
                callback_data=f"faq_{i}"
            )
        ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_faq_back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔙 К списку вопросов",
                    callback_data="faq_back"
                )
            ]
        ]
    ) 