from .methods.services import ServiceMethods
from .methods.subscriptions import SubscriptionMethods
from .methods.transactions import TransactionMethods
from .methods.users import UserMethods
from .methods.vpn_keys import VPNKeyMethods


class GoogleSheetsMethods:
    def __init__(self, connection, spreadsheet_id, crypto_key: str):
        self.client = connection.client
        self.spreadsheet = self.client.open_by_key(spreadsheet_id)

        self.users = UserMethods(self.spreadsheet)
        self.services = ServiceMethods(self.spreadsheet)
        self.transactions = TransactionMethods(self.spreadsheet, crypto_key)
        self.vpn_keys = VPNKeyMethods(self.spreadsheet)
        self.subscriptions = SubscriptionMethods(self.spreadsheet)
