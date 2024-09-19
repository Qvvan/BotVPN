from aiogram.fsm.state import State, StatesGroup


class AddKeyStates(StatesGroup):
    waiting_for_key = State()


class AnotherFeatureStates(StatesGroup):
    waiting_for_input = State()
    processing = State()
