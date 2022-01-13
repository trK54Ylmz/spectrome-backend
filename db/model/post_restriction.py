from db import Base
from sqlalchemy import Column, Integer


class PostRestriction(Base):
    __tablename__ = 'post_restrictions'

    rid = Column('id', Integer, primary_key=True, autoincrement=True)
    post_id = Column('post_id', Integer, nullable=False, index=True)
    user_id = Column('user_id', Integer, nullable=False, index=True)
