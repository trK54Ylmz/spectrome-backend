from db import Base
from sqlalchemy import Column, Integer, Index
from sqlalchemy.dialects.postgresql import ARRAY as Array, TIMESTAMP as Timestamp


class History(Base):
    __tablename__ = 'histories'

    hid = Column('id', Integer, primary_key=True, autoincrement=True)
    post_id = Column('post_id', Integer, nullable=False)
    comment_id = Column('comment_id', Integer, nullable=False)
    user_id = Column('user_id', Integer, nullable=False)
    user_ids = Column('user_ids', Array(Integer), nullable=False)
    create_time = Column('create_time', Timestamp(timezone=True), nullable=False)

    sort_index = Index('histories_create_time_idx', create_time.desc())
