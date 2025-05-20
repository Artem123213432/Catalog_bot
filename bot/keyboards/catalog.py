from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Optional
from bot.models.catalog import Category, Subcategory, Product

def get_categories_keyboard(categories: List[Category], page: int = 0, items_per_page: int = 5) -> InlineKeyboardMarkup:
    """Создает клавиатуру с категориями"""
    start_idx = page * items_per_page
    end_idx = start_idx + items_per_page
    current_categories = categories[start_idx:end_idx]
    
    keyboard = []
    for category in current_categories:
        keyboard.append([
            InlineKeyboardButton(
                text=category.name,
                callback_data=f"category_{category.id}"
            )
        ])
    
    # Добавляем кнопки навигации
    nav_buttons = []
    if page > 0:
        nav_buttons.append(
            InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data=f"categories_page_{page-1}"
            )
        )
    if end_idx < len(categories):
        nav_buttons.append(
            InlineKeyboardButton(
                text="Вперед ➡️",
                callback_data=f"categories_page_{page+1}"
            )
        )
    if nav_buttons:
        keyboard.append(nav_buttons)
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_subcategories_keyboard(subcategories: List[Subcategory], page: int = 0, items_per_page: int = 5) -> InlineKeyboardMarkup:
    """Создает клавиатуру с подкатегориями"""
    start_idx = page * items_per_page
    end_idx = start_idx + items_per_page
    current_subcategories = subcategories[start_idx:end_idx]
    
    keyboard = []
    for subcategory in current_subcategories:
        keyboard.append([
            InlineKeyboardButton(
                text=subcategory.name,
                callback_data=f"subcategory_{subcategory.id}"
            )
        ])
    
    # Добавляем кнопки навигации
    nav_buttons = []
    if page > 0:
        nav_buttons.append(
            InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data=f"subcategories_page_{page-1}"
            )
        )
    if end_idx < len(subcategories):
        nav_buttons.append(
            InlineKeyboardButton(
                text="Вперед ➡️",
                callback_data=f"subcategories_page_{page+1}"
            )
        )
    if nav_buttons:
        keyboard.append(nav_buttons)
    
    # Добавляем кнопку возврата к категориям
    keyboard.append([
        InlineKeyboardButton(
            text="🔙 К категориям",
            callback_data="back_to_categories"
        )
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_products_keyboard(products: List[Product], page: int = 0, items_per_page: int = 5) -> InlineKeyboardMarkup:
    """Создает клавиатуру с товарами"""
    start_idx = page * items_per_page
    end_idx = start_idx + items_per_page
    current_products = products[start_idx:end_idx]
    
    keyboard = []
    for product in current_products:
        keyboard.append([
            InlineKeyboardButton(
                text=f"{product.name} - ${product.price}",
                callback_data=f"product_{product.id}"
            )
        ])
    
    # Добавляем кнопки навигации
    nav_buttons = []
    if page > 0:
        nav_buttons.append(
            InlineKeyboardButton(
                text="⬅️ Назад",
                callback_data=f"products_page_{page-1}"
            )
        )
    if end_idx < len(products):
        nav_buttons.append(
            InlineKeyboardButton(
                text="Вперед ➡️",
                callback_data=f"products_page_{page+1}"
            )
        )
    if nav_buttons:
        keyboard.append(nav_buttons)
    
    # Добавляем кнопку возврата к подкатегориям
    keyboard.append([
        InlineKeyboardButton(
            text="🔙 К подкатегориям",
            callback_data="back_to_subcategories"
        )
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_product_keyboard(product: Product) -> InlineKeyboardMarkup:
    """Создает клавиатуру для отдельного товара"""
    keyboard = [
        [
            InlineKeyboardButton(
                text="🛒 Добавить в корзину",
                callback_data=f"add_to_cart_{product.id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="🔙 К товарам",
                callback_data="back_to_products"
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard) 