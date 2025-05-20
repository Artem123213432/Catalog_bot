from aiogram.fsm.state import State, StatesGroup

class CatalogStates(StatesGroup):
    """Состояния для работы с каталогом"""
    viewing_categories = State()  # Просмотр категорий
    viewing_subcategories = State()  # Просмотр подкатегорий
    viewing_products = State()  # Просмотр товаров
    viewing_product = State()  # Просмотр отдельного товара 