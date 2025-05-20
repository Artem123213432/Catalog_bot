from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
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
from bot.routers import cart
from bot.data.cart_storage import user_carts
import logging

router = Router()
logger = logging.getLogger(__name__)

def find_category(category_id: int) -> tuple[Category, int]:
    """Находит категорию по ID и возвращает её и индекс"""
    for i, category in enumerate(CATEGORIES):
        if category.id == category_id:
            return category, i
    raise ValueError(f"Category with id {category_id} not found")

def find_subcategory(category: Category, subcategory_id: int) -> tuple[Subcategory, int]:
    """Находит подкатегорию по ID и возвращает её и индекс"""
    for i, subcategory in enumerate(category.subcategories):
        if subcategory.id == subcategory_id:
            return subcategory, i
    raise ValueError(f"Subcategory with id {subcategory_id} not found")

def find_product(subcategory: Subcategory, product_id: int) -> tuple[Product, int]:
    """Находит товар по ID и возвращает его и индекс"""
    for i, product in enumerate(subcategory.products):
        if product.id == product_id:
            return product, i
    raise ValueError(f"Product with id {product_id} not found")

@router.message(Command("catalog"))
async def cmd_catalog(message: Message, state: FSMContext):
    """Обработчик команды /catalog"""
    await state.set_state(CatalogStates.viewing_categories)
    await message.answer(
        "Выберите категорию:",
        reply_markup=get_categories_keyboard(CATEGORIES)
    )

@router.callback_query(CatalogStates.viewing_categories, F.data.startswith("category_"))
async def process_category_selection(callback: CallbackQuery, state: FSMContext):
    """Обработчик выбора категории"""
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
    """Обработчик пагинации категорий"""
    page = int(callback.data.split("_")[2])
    await callback.message.edit_text(
        "Выберите категорию:",
        reply_markup=get_categories_keyboard(CATEGORIES, page)
    )

@router.callback_query(CatalogStates.viewing_subcategories, F.data.startswith("subcategory_"))
async def process_subcategory_selection(callback: CallbackQuery, state: FSMContext):
    """Обработчик выбора подкатегории"""
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
    """Обработчик пагинации подкатегорий"""
    page = int(callback.data.split("_")[2])
    data = await state.get_data()
    category, _ = find_category(data["current_category_id"])
    
    await callback.message.edit_text(
        f"Категория: {category.name}\nВыберите подкатегорию:",
        reply_markup=get_subcategories_keyboard(category.subcategories, page)
    )

@router.callback_query(CatalogStates.viewing_subcategories, F.data == "back_to_categories")
async def process_back_to_categories(callback: CallbackQuery, state: FSMContext):
    """Обработчик возврата к категориям"""
    await state.set_state(CatalogStates.viewing_categories)
    await callback.message.edit_text(
        "Выберите категорию:",
        reply_markup=get_categories_keyboard(CATEGORIES)
    )

@router.callback_query(CatalogStates.viewing_products, F.data.startswith("product_"))
async def process_product_selection(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик выбора товара
    """
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
        
        # Удаляем сообщение с товарами перед отправкой карточки товара
        await callback.message.delete()

        await callback.message.answer_photo(
            photo=product.image_url,
            caption=f"<b>{product.name}</b>\n\n{product.description}\n\nЦена: ${product.price}",
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
        # Всегда отвечаем на callback, чтобы убрать часики загрузки
        await callback.answer()

@router.callback_query(CatalogStates.viewing_products, F.data.startswith("products_page_"))
async def process_products_pagination(callback: CallbackQuery, state: FSMContext):
    """Обработчик пагинации товаров"""
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
    """Обработчик возврата к подкатегориям"""
    data = await state.get_data()
    category, _ = find_category(data["current_category_id"])
    
    await state.set_state(CatalogStates.viewing_subcategories)
    await callback.message.edit_text(
        f"Категория: {category.name}\nВыберите подкатегорию:",
        reply_markup=get_subcategories_keyboard(category.subcategories)
    )

@router.callback_query(CatalogStates.viewing_product, F.data.startswith("add_to_cart_"))
async def process_add_to_cart(callback: CallbackQuery, state: FSMContext):
    """
    Обработчик добавления товара в корзину
    """
    try:
        # Получаем ID пользователя и информацию о товаре
        user_id = callback.from_user.id
        product_id = int(callback.data.split("_")[3])
        data = await state.get_data()
        category, _ = find_category(data["current_category_id"])
        subcategory, _ = find_subcategory(category, data["current_subcategory_id"])
        product, _ = find_product(subcategory, product_id)
        
        # Инициализируем корзину пользователя, если её нет
        if user_id not in user_carts:
            user_carts[user_id] = []
            
        # Добавляем товар в корзину (можно добавить логику для количества, если нужно)
        user_carts[user_id].append({
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "quantity": 1 # Пока добавляем по одной штуке
        })
        
        logger.info(f"Товар {product.name} (ID: {product.id}) добавлен в корзину пользователя {user_id}")

        await callback.answer("Товар добавлен в корзину!", show_alert=True)
        
    except Exception as e:
        logger.error(f"Ошибка при добавлении товара в корзину: {e}", exc_info=True)
        await callback.answer(
            "Произошла ошибка при добавлении товара в корзину. Попробуйте позже.",
            show_alert=True
        )

@router.callback_query(CatalogStates.viewing_product, F.data == "back_to_products")
async def process_back_to_products(callback: CallbackQuery, state: FSMContext):
    """Обработчик возврата к товарам"""
    data = await state.get_data()
    category, _ = find_category(data["current_category_id"])
    subcategory, _ = find_subcategory(category, data["current_subcategory_id"])
    
    await state.set_state(CatalogStates.viewing_products)
    await callback.message.delete()
    await callback.message.answer(
        f"Подкатегория: {subcategory.name}\nВыберите товар:",
        reply_markup=get_products_keyboard(subcategory.products)
    ) 