from db import Base
from sqlalchemy import Column, Integer, String, TIMESTAMP as Timestamp


class Forgot(Base):
    __tablename__ = 'forgots'

    fid = Column('id', Integer, primary_key=True, autoincrement=True)
    user_id = Column('user_id', Integer, nullable=False, index=True)
    code = Column('code', String(6), index=True)
    token = Column('token', String(100), nullable=False)
    create_time = Column('create_time', Timestamp(timezone=True), nullable=False)
