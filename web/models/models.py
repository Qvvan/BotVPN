from sqlalchemy import Column, Integer, String, BigInteger
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Subscription(Base):
    __tablename__ = 'subscriptions'

    subscription_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(BigInteger, index=True)
    status = Column(String)


class Server(Base):
    __tablename__ = 'servers'

    server_id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    api_url = Column(String)
    cert_sha256 = Column(String)
    limit = Column(Integer)
