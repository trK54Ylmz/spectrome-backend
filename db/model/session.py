from db import Base
from sqlalchemy import Column, Integer, String, TIMESTAMP as Timestamp


class SessionToken(Base):
    __tablename__ = 'session_tokens'

    user_id = Column('uid', Integer, primary_key=True)
    token = Column('token', String(200), nullable=False)
    create_time = Column('create_time', Timestamp(timezone=True), nullable=False)
