from datetime import datetime

from sqlalchemy import Column, String, Integer, DateTime, Enum, BigInteger, ARRAY
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class SubscriptionStatusEnum(str, Enum):
    ACTIVE = 'активная'
    EXPIRED = 'истекла'
    CANCELED = 'отменена'


class NameApp(str, Enum):
    OUTLINE = 'Outline'
    VLESS = 'Vless'


class StatusSubscriptionHistory(str, Enum):
    NEW_SUBSCRIPTION = 'новая подписка'
    EXTENSION = 'продление'


class Users(Base):
    __tablename__ = 'users'

    user_id = Column(BigInteger, primary_key=True, nullable=False)
    username = Column(String)
    ban = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class Services(Base):
    __tablename__ = 'services'

    service_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    duration_days = Column(Integer, nullable=False)
    price = Column(Integer, nullable=False)


class Subscriptions(Base):
    __tablename__ = 'subscriptions'

    subscription_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False)
    service_id = Column(Integer, nullable=True)
    key = Column(String, nullable=True)
    key_id = Column(Integer, nullable=True)
    server_ip = Column(String, nullable=True)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    status = Column(String, default=SubscriptionStatusEnum.ACTIVE)
    name_app = Column(String, nullable=True)
    reminder_sent = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SubscriptionsHistory(Base):
    __tablename__ = 'subscriptions_history'

    subscription_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=True)
    service_id = Column(Integer, nullable=True)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    status = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Transactions(Base):
    __tablename__ = 'transactions'

    transaction_id = Column(Integer, primary_key=True, autoincrement=True)
    transaction_code = Column(String, unique=True, nullable=False)
    service_id = Column(Integer, nullable=False)
    user_id = Column(BigInteger, nullable=False)
    status = Column(String)
    description = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Servers(Base):
    __tablename__ = 'servers'

    server_ip = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    limit = Column(Integer, nullable=True)
    hidden = Column(Integer, nullable=True, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class Pushes(Base):
    __tablename__ = 'pushes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    message = Column(String, nullable=False)
    user_ids = Column(ARRAY(Integer), default=[])
    timestamp = Column(DateTime, default=datetime.utcnow)
