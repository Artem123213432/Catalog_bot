from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from bot.keyboards.inline import get_subscription_keyboard, get_welcome_keyboard
from bot.utils.subscription import check_subscription
from bot.config import Config
import logging

from bot.routers.catalog import cmd_catalog
from bot.routers.cart import cmd_cart
from bot.routers.faq import show_faq

logger = logging.getLogger(__name__)
router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message):
    is_subscribed = await check_subscription(
        bot=message.bot,
        user_id=message.from_user.id,
        channels=[Config.CHANNEL_USERNAME]
    )
    
    if is_subscribed:
        await message.answer(
            f"Добро пожаловать, {message.from_user.full_name}! Я ваш бот-помощник в мире товаров. Выберите, что вас интересует:",
            reply_markup=get_welcome_keyboard()
        )
    else:
        await message.answer(
            "Для использования бота необходимо подписаться на канал!",
            reply_markup=get_subscription_keyboard()
        )

@router.callback_query(F.data == "check_subscription")
async def check_subscription_callback(callback: CallbackQuery):
    try:
        logger.info(f"Проверка подписки для пользователя {callback.from_user.id}")
        
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
                f"Добро пожаловать, {callback.from_user.full_name}! Я ваш бот-помощник в мире товаров. Выберите, что вас интересует:",
                reply_markup=get_welcome_keyboard()
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

@router.callback_query(F.data == "show_catalog")
async def handle_show_catalog(callback: CallbackQuery, state):
    await callback.answer()
    await cmd_catalog(callback.message, state)

@router.callback_query(F.data == "show_cart")
async def handle_show_cart(callback: CallbackQuery):
    await callback.answer()
    await cmd_cart(callback.message)

@router.callback_query(F.data == "show_faq")
async def handle_show_faq(callback: CallbackQuery):
    await callback.answer()
    await show_faq(callback.message)
