from .methods.services import ServiceMethods
from .methods.subscriptions import SubscriptionMethods
from .methods.transactions import TransactionMethods
from .methods.users import UserMethods
from .methods.vpn_keys import VPNKeyMethods

class PostgresMethods:
    def __init__(self, connection):
        self.connection = connection

        self.users = UserMethods(self.connection)
        self.services = ServiceMethods(self.connection)
        self.transactions = TransactionMethods(self.connection)
        self.vpn_keys = VPNKeyMethods(self.connection)
        self.subscriptions = SubscriptionMethods(self.connection)
