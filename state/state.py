from aiogram.fsm.state import State, StatesGroup


class AddKeyStates(StatesGroup):
    waiting_for_server = State()
    waiting_for_key = State()


class CancelTransaction(StatesGroup):
    waiting_for_transaction = State()


class ChoiceServer(StatesGroup):
    waiting_for_choice = State()
    waiting_for_services = State()


class AddAdmin(StatesGroup):
    waiting_apiUrl = State()
    waiting_certSha256 = State()


class DeleteKey(StatesGroup):
    waiting_key_code = State()


class KeyInfo(StatesGroup):
    waiting_key_info = State()


class KeyBlock(StatesGroup):
    waiting_key_block = State()


class UnblockKey(StatesGroup):
    waiting_key_unblock = State()


class CancelSub(StatesGroup):
    waiting_user_id = State()
