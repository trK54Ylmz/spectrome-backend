from db import Base
from server.message import BaseMessage
from sqlalchemy import Boolean, Column, Index, Integer, String, TIMESTAMP as Timestamp


class Comment(Base):
    __tablename__ = 'comments'

    cid = Column('id', Integer, primary_key=True, autoincrement=True)
    post_id = Column('post_id', Integer, nullable=False, index=True)
    user_id = Column('user_id', Integer, nullable=False, index=True)
    code = Column('code', String(40), unique=True)
    message = Column('message', String(1024), nullable=False)
    owned = Column('owned', Boolean, nullable=False, default=False)
    create_time = Column('create_time', Timestamp(timezone=True), nullable=False)

    sort_index = Index('comments_create_time_idx', create_time.desc())

    def to_json(self):
        """
        Return database instance as json object

        :return: json response as dictionary
        :rtype: dict
        """
        msg = BaseMessage()
        msg.code = self.code
        msg.message = self.message
        msg.create_time = self.create_time.isoformat()

        return msg.to_json()
