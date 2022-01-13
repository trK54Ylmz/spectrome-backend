from db import Base
from sqlalchemy import Boolean, Column, Integer, String, TIMESTAMP as Timestamp


class Intention(Base):
    __tablename__ = 'intentions'

    fid = Column('id', Integer, primary_key=True, autoincrement=True)
    from_id = Column('from_id', Integer, nullable=False)
    to_id = Column('to_id', Integer, nullable=False)
    code = Column('code', String(64), nullable=False, index=True)
    sent = Column('sent', Boolean, nullable=False, index=True)
    create_time = Column('create_time', Timestamp(timezone=True), nullable=False)
