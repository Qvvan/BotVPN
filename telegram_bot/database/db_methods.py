from telegram_bot.database.methods import services, users, subscriptions, server, transactions


class MethodsManager:
    def __init__(self, session):
        self.session = session

        self.users = users.UserMethods(self.session)
        self.transactions = transactions.TransactionMethods(self.session)
        self.subscription = subscriptions.SubscriptionMethods(self.session)
        self.services = services.ServiceMethods(self.session)
        self.servers = server.ServerMethods(self.session)
