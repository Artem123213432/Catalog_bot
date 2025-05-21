from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from bot.states.cart import CartStates
from bot.models.catalog import CATEGORIES, Product
from bot.keyboards.catalog import get_product_keyboard
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
from bot.utils.excel_handler import save_order
from bot.utils.payment import create_payment, check_payment
import asyncio
from bot.data.cart_storage import user_carts
import logging

router = Router()
logger = logging.getLogger(__name__)

DJANGO_API_URL = "http://admin_panel:8000/api/orders/"

def get_cart_keyboard(cart):
    keyboard = []
    for idx, item in enumerate(cart):
        keyboard.append([
            InlineKeyboardButton(
                text=f"❌ Удалить {item['name']}",
                callback_data=f"remove_{idx}"
            )
        ])
    if cart:
        keyboard.append([
            InlineKeyboardButton(text="✅ Оформить заказ", callback_data="checkout")
        ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard) if cart else None

@router.message(Command("cart"))
async def cmd_cart(message: Message):
    try:
        user_id = message.from_user.id
        cart = user_carts.get(user_id, [])
        if not cart:
            await message.answer("Ваша корзина пуста.")
            return
        text = "\n".join([f"<b>{item['name']}</b> — {item['price']} ₽" for item in cart])
        total = sum(item['price'] for item in cart)
        await message.answer(f"Ваша корзина:\n{text}\n\nИтого: {total} ₽", reply_markup=get_cart_keyboard(cart))
    except Exception as e:
        logger.error(f"Ошибка при отображении корзины: {e}", exc_info=True)
        await message.answer("Произошла ошибка при отображении корзины. Попробуйте позже.")

@router.callback_query(F.data.startswith("add_to_cart_"))
async def add_to_cart(callback: CallbackQuery):
    user_id = callback.from_user.id
    product_id = int(callback.data.split("_")[3])
    
    for category in CATEGORIES:
        for subcategory in category.subcategories:
            for product in subcategory.products:
                if product.id == product_id:
                    user_carts.setdefault(user_id, []).append({
                        "id": product.id,
                        "name": product.name,
                        "price": product.price
                    })
                    await callback.answer("Товар добавлен в корзину!")
                    return
    await callback.answer("Товар не найден", show_alert=True)

@router.callback_query(F.data.startswith("remove_"))
async def remove_from_cart(callback: CallbackQuery):
    user_id = callback.from_user.id
    idx = int(callback.data.split("_")[1])
    cart = user_carts.get(user_id, [])
    if 0 <= idx < len(cart):
        removed = cart.pop(idx)
        await callback.answer(f"{removed['name']} удалён из корзины")
    else:
        await callback.answer("Ошибка удаления", show_alert=True)
    
    if cart:
        text = "\n".join([f"<b>{item['name']}</b> — {item['price']} ₽" for item in cart])
        total = sum(item['price'] for item in cart)
        await callback.message.edit_text(f"Ваша корзина:\n{text}\n\nИтого: {total} ₽", reply_markup=get_cart_keyboard(cart))
    else:
        await callback.message.edit_text("Ваша корзина пуста.")

@router.callback_query(F.data == "checkout")
async def checkout(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    cart = user_carts.get(user_id, [])
    if not cart:
        await callback.answer("Корзина пуста", show_alert=True)
        return
    await state.set_state(CartStates.waiting_for_name)
    await callback.message.answer("Введите ваше имя:")

@router.message(CartStates.waiting_for_name)
async def get_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(CartStates.waiting_for_phone)
    await message.answer("Введите ваш номер телефона:")

@router.message(CartStates.waiting_for_phone)
async def get_phone(message: Message, state: FSMContext):
    await state.update_data(phone=message.text)
    await state.set_state(CartStates.waiting_for_address)
    await message.answer("Введите адрес доставки:")

@router.message(CartStates.waiting_for_address)
async def get_address(message: Message, state: FSMContext):
    await state.update_data(address=message.text)
    data = await state.get_data()
    text = (
        f"<b>Проверьте данные заказа:</b>\n"
        f"Имя: {data['name']}\n"
        f"Телефон: {data['phone']}\n"
        f"Адрес: {data['address']}\n\n"
        f"Подтвердить заказ? (да/нет)"
    )
    await state.set_state(CartStates.confirming)
    await message.answer(text)

@router.message(CartStates.confirming)
async def confirm_order(message: Message, state: FSMContext):
    if message.text.lower() not in ("да", "yes", "y"): 
        await message.answer("Заказ отменён.")
        await state.clear()
        return
    
    try:
        data = await state.get_data()
        user_id = message.from_user.id
        cart = user_carts.get(user_id, [])
        
        
        order_data = {
            "client": {
                "name": data['name'],
                "phone": data['phone'],
                "address": data['address']
            },
            "items": [
                {
                    "product_id": item.get("id"),
                    "quantity": item.get("quantity", 1),
                    "name": item.get("name"),
                    "price": item.get("price")
                } for item in cart
            ]
        }
        
        
        save_order(order_data)
        
        
        total_sum = sum(item['price'] * item['quantity'] for item in cart)
        payment = await create_payment(
            amount=total_sum,
            description=f"Заказ от {data['name']}"
        )
        
        
        await state.update_data(payment_id=payment['id'])
        
        
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="💳 Оплатить заказ", url=payment['payment_url'])]
        ])
        
        await message.answer(
            f"Ваш заказ оформлен!\n\n"
            f"Сумма к оплате: {total_sum} ₽\n"
            f"Для завершения заказа, пожалуйста, оплатите его по ссылке ниже:",
            reply_markup=keyboard
        )
        
        
        user_carts[user_id] = []
        await state.clear()
        
    except Exception as e:
        logger.error(f"Ошибка при оформлении заказа: {e}")
        await message.answer("Произошла ошибка при оформлении заказа. Попробуйте позже.")
        await state.clear()

async def check_payment_status(message: Message, state: FSMContext, payment_id: str):
    for _ in range(30):  
        payment = await check_payment(payment_id)
        if payment and payment['paid']:
            await message.answer(
                "✅ Оплата прошла успешно!\n"
                "Спасибо за заказ! Мы свяжемся с вами в ближайшее время."
            )
            
            user_id = message.from_user.id
            user_carts[user_id] = []
            await state.clear()
            return
        await asyncio.sleep(10)
    
    await message.answer(
        "⚠️ Время ожидания оплаты истекло.\n"
        "Если вы уже оплатили заказ, пожалуйста, свяжитесь с поддержкой."
    )

def send_order_to_django(order_data):
    try:
        response = requests.post(DJANGO_API_URL, json=order_data, timeout=5)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Ошибка при отправке заказа в Django: {e}")
        return None 