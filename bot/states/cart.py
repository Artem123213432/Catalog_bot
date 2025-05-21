from aiogram.fsm.state import State, StatesGroup

class CartStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_address = State()
    waiting_for_phone = State()
    confirming = State() 