from aiogram.dispatcher.filters.state import State, StatesGroup


class MenuState(StatesGroup):
    training = State()
    dialog = State()
