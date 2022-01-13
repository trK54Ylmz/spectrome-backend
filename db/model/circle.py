from db import Base
from sqlalchemy import Column, Integer, TIMESTAMP as Timestamp


class Circle(Base):
    __tablename__ = 'circles'

    fid = Column('id', Integer, primary_key=True, autoincrement=True)
    from_id = Column('from_id', Integer, nullable=False, index=True)
    to_id = Column('to_id', Integer, nullable=False, index=True)
    create_time = Column('create_time', Timestamp(timezone=True), nullable=False)
