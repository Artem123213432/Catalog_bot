from aiogram.fsm.state import State, StatesGroup

class CatalogStates(StatesGroup):
    viewing_categories = State()  
    viewing_subcategories = State()  
    viewing_products = State()  
    viewing_product = State()  