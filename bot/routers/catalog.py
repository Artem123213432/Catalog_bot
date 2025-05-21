from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state

from bot.states.catalog import CatalogStates
from bot.models.catalog import CATEGORIES, Category, Subcategory, Product
from bot.keyboards.catalog import (
    get_categories_keyboard,
    get_subcategories_keyboard,
    get_products_keyboard,
    get_product_keyboard
)
from bot.routers.cart import cmd_cart
from bot.data.cart_storage import user_carts
import logging

router = Router()
logger = logging.getLogger(__name__)

def find_category(category_id: int) -> tuple[Category, int]:
    for i, category in enumerate(CATEGORIES):
        if category.id == category_id:
            return category, i
    raise ValueError(f"Category with id {category_id} not found")

def find_subcategory(category: Category, subcategory_id: int) -> tuple[Subcategory, int]:
    for i, subcategory in enumerate(category.subcategories):
        if subcategory.id == subcategory_id:
            return subcategory, i
    raise ValueError(f"Subcategory with id {subcategory_id} not found")

def find_product(subcategory: Subcategory, product_id: int) -> tuple[Product, int]:
    for i, product in enumerate(subcategory.products):
        if product.id == product_id:
            return product, i
    raise ValueError(f"Product with id {product_id} not found")

@router.message(Command("catalog"))
async def cmd_catalog(message: Message, state: FSMContext):
    await state.set_state(CatalogStates.viewing_categories)
    await message.answer(
        "Выберите категорию:",
        reply_markup=get_categories_keyboard(CATEGORIES)
    )

@router.callback_query(CatalogStates.viewing_categories, F.data.startswith("category_"))
async def process_category_selection(callback: CallbackQuery, state: FSMContext):
    category_id = int(callback.data.split("_")[1])
    category, _ = find_category(category_id)
    
    await state.set_state(CatalogStates.viewing_subcategories)
    await state.update_data(current_category_id=category_id)
    
    await callback.message.edit_text(
        f"Категория: {category.name}\nВыберите подкатегорию:",
        reply_markup=get_subcategories_keyboard(category.subcategories)
    )

@router.callback_query(CatalogStates.viewing_categories, F.data.startswith("categories_page_"))
async def process_categories_pagination(callback: CallbackQuery):
    page = int(callback.data.split("_")[2])
    await callback.message.edit_text(
        "Выберите категорию:",
        reply_markup=get_categories_keyboard(CATEGORIES, page)
    )

@router.callback_query(CatalogStates.viewing_subcategories, F.data.startswith("subcategory_"))
async def process_subcategory_selection(callback: CallbackQuery, state: FSMContext):
    subcategory_id = int(callback.data.split("_")[1])
    data = await state.get_data()
    category, _ = find_category(data["current_category_id"])
    subcategory, _ = find_subcategory(category, subcategory_id)
    
    await state.set_state(CatalogStates.viewing_products)
    await state.update_data(current_subcategory_id=subcategory_id)
    
    await callback.message.edit_text(
        f"Подкатегория: {subcategory.name}\nВыберите товар:",
        reply_markup=get_products_keyboard(subcategory.products)
    )

@router.callback_query(CatalogStates.viewing_subcategories, F.data.startswith("subcategories_page_"))
async def process_subcategories_pagination(callback: CallbackQuery, state: FSMContext):
    page = int(callback.data.split("_")[2])
    data = await state.get_data()
    category, _ = find_category(data["current_category_id"])
    
    await callback.message.edit_text(
        f"Категория: {category.name}\nВыберите подкатегорию:",
        reply_markup=get_subcategories_keyboard(category.subcategories, page)
    )

@router.callback_query(CatalogStates.viewing_subcategories, F.data == "back_to_categories")
async def process_back_to_categories(callback: CallbackQuery, state: FSMContext):
    await state.set_state(CatalogStates.viewing_categories)
    await callback.message.edit_text(
        "Выберите категорию:",
        reply_markup=get_categories_keyboard(CATEGORIES)
    )

@router.callback_query(CatalogStates.viewing_products, F.data.startswith("product_"))
async def process_product_selection(callback: CallbackQuery, state: FSMContext):
    try:
        product_id = int(callback.data.split("_")[1])
        logger.info(f"Выбран товар с ID: {product_id}")
        
        data = await state.get_data()
        category, _ = find_category(data["current_category_id"])
        subcategory, _ = find_subcategory(category, data["current_subcategory_id"])
        product, _ = find_product(subcategory, product_id)
        
        logger.info(f"Найден товар: {product.name}, ID: {product.id}")

        await state.set_state(CatalogStates.viewing_product)
        await state.update_data(current_product_id=product_id)
        
        
        await callback.message.delete()

        await callback.message.answer_photo(
            photo=product.image_url,
            caption=f"<b>{product.name}</b>\n\n{product.description}\n\nЦена: {product.price} ₽",
            reply_markup=get_product_keyboard(product)
        )
        logger.info(f"Отправлена карточка товара: {product.name}")
        
    except Exception as e:
        logger.error(f"Ошибка при обработке выбора товара: {e}", exc_info=True)
        await callback.answer(
            "Произошла ошибка при загрузке товара. Попробуйте позже.",
            show_alert=True
        )
        
    finally:
        
        await callback.answer()

@router.callback_query(CatalogStates.viewing_products, F.data.startswith("products_page_"))
async def process_products_pagination(callback: CallbackQuery, state: FSMContext):
    page = int(callback.data.split("_")[2])
    data = await state.get_data()
    category, _ = find_category(data["current_category_id"])
    subcategory, _ = find_subcategory(category, data["current_subcategory_id"])
    
    await callback.message.edit_text(
        f"Подкатегория: {subcategory.name}\nВыберите товар:",
        reply_markup=get_products_keyboard(subcategory.products, page)
    )

@router.callback_query(CatalogStates.viewing_products, F.data == "back_to_subcategories")
async def process_back_to_subcategories(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    category, _ = find_category(data["current_category_id"])
    
    await state.set_state(CatalogStates.viewing_subcategories)
    await callback.message.edit_text(
        f"Категория: {category.name}\nВыберите подкатегорию:",
        reply_markup=get_subcategories_keyboard(category.subcategories)
    )


def get_quantity_keyboard(product_id: int, quantity: int = 1) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton(text="-", callback_data=f"decrease_quantity_{product_id}"),
            InlineKeyboardButton(text=str(quantity), callback_data=f"quantity_{product_id}_{quantity}"),
            InlineKeyboardButton(text="+", callback_data=f"increase_quantity_{product_id}")
        ],
        [
            InlineKeyboardButton(text="❌ Отмена", callback_data="cancel_quantity")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


@router.callback_query(CatalogStates.viewing_product, F.data.startswith("choose_quantity_"))
async def process_choose_quantity(callback: CallbackQuery, state: FSMContext):
    product_id = int(callback.data.split("_")[2])
    await state.update_data(quantity=1)
    await callback.message.edit_reply_markup(reply_markup=get_quantity_keyboard(product_id))
    await callback.answer()


@router.callback_query(CatalogStates.viewing_product, F.data.startswith("increase_quantity_"))
async def process_increase_quantity(callback: CallbackQuery, state: FSMContext):
    product_id = int(callback.data.split("_")[2])
    data = await state.get_data()
    current_quantity = data.get("quantity", 1)
    new_quantity = current_quantity + 1
    await state.update_data(quantity=new_quantity)
    await callback.message.edit_reply_markup(reply_markup=get_quantity_keyboard(product_id, new_quantity))
    await callback.answer()


@router.callback_query(CatalogStates.viewing_product, F.data.startswith("decrease_quantity_"))
async def process_decrease_quantity(callback: CallbackQuery, state: FSMContext):
    product_id = int(callback.data.split("_")[2])
    data = await state.get_data()
    current_quantity = data.get("quantity", 1)
    new_quantity = max(1, current_quantity - 1)
    await state.update_data(quantity=new_quantity)
    await callback.message.edit_reply_markup(reply_markup=get_quantity_keyboard(product_id, new_quantity))
    await callback.answer()


@router.callback_query(CatalogStates.viewing_product, F.data.startswith("quantity_"))
async def process_add_to_cart_with_quantity(callback: CallbackQuery, state: FSMContext):
    try:
        user_id = callback.from_user.id
        _, product_id, quantity = callback.data.split("_")
        product_id = int(product_id)
        quantity = int(quantity)
        data = await state.get_data()
        category, _ = find_category(data["current_category_id"])
        subcategory, _ = find_subcategory(category, data["current_subcategory_id"])
        product, _ = find_product(subcategory, product_id)
        if user_id not in user_carts:
            user_carts[user_id] = []
        user_carts[user_id].append({
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "quantity": quantity
        })
        await callback.message.edit_reply_markup(reply_markup=get_product_keyboard(product))
        await callback.answer(f"Добавлено в корзину: {product.name} x{quantity}", show_alert=True)
    except Exception as e:
        logger.error(f"Ошибка при добавлении товара с количеством: {e}", exc_info=True)
        await callback.answer("Ошибка при добавлении товара. Попробуйте позже.", show_alert=True)


@router.callback_query(CatalogStates.viewing_product, F.data == "cancel_quantity")
async def process_cancel_quantity(callback: CallbackQuery):
    await callback.message.edit_reply_markup(reply_markup=get_product_keyboard)
    await callback.answer("Отменено")

@router.callback_query(F.data == "view_cart")
async def process_view_cart(callback: CallbackQuery):
    try:
        user_id = callback.from_user.id
        cart = user_carts.get(user_id, [])
        if not cart:
            await callback.message.answer("Ваша корзина пуста.")
            return
        from bot.routers.cart import get_cart_keyboard
        text = "\n".join([f"<b>{item['name']}</b> — {item['price']} ₽ x{item['quantity']}" for item in cart])
        total = sum(item['price'] * item['quantity'] for item in cart)
        await callback.message.answer(f"Ваша корзина:\n{text}\n\nИтого: {total} ₽", reply_markup=get_cart_keyboard(cart))
    except Exception as e:
        logger.error(f"Ошибка при переходе в корзину: {e}", exc_info=True)
        await callback.answer(
            "Произошла ошибка при переходе в корзину. Попробуйте позже.",
            show_alert=True
        )
    finally:
        await callback.answer() 