from datetime import datetime

from sqlalchemy import Column, String, Integer, DateTime, Enum, BigInteger
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class SubscriptionStatusEnum(str, Enum):
    ACTIVE = 'активная'
    EXPIRED = 'истекла'
    CANCELED = 'отменена'


class Users(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    tg_id = Column(BigInteger, unique=True, index=True, nullable=False)
    username = Column(String)
    ban = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class Services(Base):
    __tablename__ = 'services'

    service_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    duration_days = Column(Integer, nullable=False)
    price = Column(Integer, nullable=False)


class VPNKeys(Base):
    __tablename__ = 'vpn_keys'

    vpn_key_id = Column(Integer, primary_key=True, autoincrement=True)
    outline_key_id = Column(String, nullable=False)
    server_id = Column(String, nullable=False)
    key = Column(String, unique=True, nullable=False)
    server_name = Column(String, nullable=False)
    issued_at = Column(DateTime, default=None)
    is_active = Column(Integer, default=False)
    is_limit = Column(Integer, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Subscriptions(Base):
    __tablename__ = 'subscriptions'

    subscription_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, nullable=False)
    service_id = Column(Integer, nullable=False)
    vpn_key_id = Column(Integer, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    status = Column(String, default=SubscriptionStatusEnum.ACTIVE)
    reminder_sent = Column(Integer, default=0)
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

    server_id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    api_url = Column(String, unique=True, nullable=False)
    cert_sha256 = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
