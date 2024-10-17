from aiogram.fsm.state import State
from aiogram.fsm.state import StatesGroup

class GetData(StatesGroup):
    pass


class Manage(StatesGroup):
    pass


class Admin(StatesGroup):
    get_data = GetData
    manage = Manage
    exit = State()
