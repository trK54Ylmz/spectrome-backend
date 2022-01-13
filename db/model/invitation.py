from db import Base
from sqlalchemy import Column, Integer, String, TIMESTAMP as Timestamp


class Invitation(Base):
    __tablename__ = 'invitations'

    iid = Column('id', Integer, primary_key=True, autoincrement=True)
    user_id = Column('user_id', Integer, nullable=False, index=True)
    email = Column('email', String(150), nullable=False)
    code = Column('code', String(100), nullable=False, index=True)
    create_time = Column('create_time', Timestamp(timezone=True), nullable=False)
