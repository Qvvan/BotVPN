from datetime import datetime

from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Users(Base):
    __tablename__ = 'users'

    user_id = Column(Integer, primary_key=True, autoincrement=True)
    tg_id = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, nullable=False)
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
    key = Column(String, unique=True, nullable=False)
    issued_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    is_blocked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class Subscriptions(Base):
    __tablename__ = 'subscriptions'

    subscription_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    service_id = Column(Integer, ForeignKey('services.service_id'), nullable=False)
    vpn_key_id = Column(Integer, ForeignKey('vpn_keys.vpn_key_id'), nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class Logs(Base):
    __tablename__ = 'logs'

    log_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    action = Column(String, nullable=False)
    details = Column(String, nullable=False)  # Convert dictionary to JSON string
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class Transactions(Base):
    __tablename__ = 'transactions'

    transaction_id = Column(Integer, primary_key=True, autoincrement=True)
    transaction_code = Column(String, unique=True, nullable=False)
    service_id = Column(Integer, ForeignKey('services.service_id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    status = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
