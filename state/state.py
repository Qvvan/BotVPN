from aiogram.fsm.state import State, StatesGroup


class AddKeyStates(StatesGroup):
    waiting_for_key = State()


class CancelTransaction(StatesGroup):
    waiting_for_transaction = State()
    processing = State()
