from aiogram.fsm.state import State, StatesGroup


class AddKeyStates(StatesGroup):
    waiting_for_server = State()
    waiting_for_key = State()


class CancelTransaction(StatesGroup):
    waiting_for_transaction = State()


class ChoiceService(StatesGroup):
    waiting_for_choice = State()
    waiting_for_services = State()


class ChoiceServer(StatesGroup):
    waiting_for_choice = State()


class AddAdmin(StatesGroup):
    waiting_ip = State()
    waiting_name = State()
    waiting_limit = State()


class DeleteKey(StatesGroup):
    waiting_key_code = State()


class KeyInfo(StatesGroup):
    waiting_key_info = State()


class KeyBlock(StatesGroup):
    waiting_key_block = State()


class UnblockKey(StatesGroup):
    waiting_key_unblock = State()


class BanUser(StatesGroup):
    waiting_user_id = State()


class UnbanUser(StatesGroup):
    waiting_user_id = State()


class ChoiceApp(StatesGroup):
    waiting_choice_app = State()


class ServerManagementStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_limit = State()
