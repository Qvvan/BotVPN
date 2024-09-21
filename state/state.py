from aiogram.fsm.state import State, StatesGroup


class AddKeyStates(StatesGroup):
    waiting_for_server = State()
    waiting_for_key = State()


class CancelTransaction(StatesGroup):
    waiting_for_transaction = State()


class ChoiceServer(StatesGroup):
    waiting_for_choice = State()
    waiting_for_services = State()
