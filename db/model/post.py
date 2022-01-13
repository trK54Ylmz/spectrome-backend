import pytz
from db import Base
from server.message import BaseMessage
from sqlalchemy import Boolean, Column, Index, Integer, String, SmallInteger
from sqlalchemy.dialects.postgresql import ARRAY as Array, TIMESTAMP as Timestamp
from util.config import config


class PostStatus:
    UPLOADED = 1
    PROCESSING = 2
    CREATED = 3
    ACTIVATED = 4
    BANNED = 5
    FAILED = 6
    DELETED = 9


class PostType:
    PHOTO = 1
    VIDEO = 2


class PostSize:
    SHORT = 1
    SQUARE = 2
    TALL = 3


class Post(Base):
    __tablename__ = 'posts'

    pid = Column('id', Integer, primary_key=True, autoincrement=True)
    user_id = Column('user_id', Integer, nullable=False, index=True)
    code = Column('code', String(40), unique=True)
    items = Column('items', Array(String(64)), nullable=False)
    types = Column('types', Array(SmallInteger), nullable=False)
    size = Column('size', SmallInteger, nullable=False)
    disposable = Column('disposable', Boolean, nullable=False)
    number_of_comments = Column('comments', Integer, default=0)
    number_of_users = Column('users', Integer, default=0)
    status = Column('status', SmallInteger, default=PostStatus.CREATED)
    create_time = Column('create_time', Timestamp(timezone=True), nullable=False)

    sort_index = Index(
        'posts_create_time_idx',
        create_time.desc(),
        postgresql_where=(status == PostStatus.ACTIVATED),
    )

    def to_json(self):
        """
        Return database instance as json object

        :return: json response as dictionary
        :rtype: dict
        """
        items = []

        for item in self.items:
            ext = 'mp4' if item == PostType.VIDEO else 'jpg'
            scheme = 'http' if config.app.debug else 'https'
            domain = config.app.cdn
            it = f'{scheme}://{domain}/post/{self.code}/{item}.thumb.{ext}'
            il = f'{scheme}://{domain}/post/{self.code}/{item}.large.{ext}'

            item = {
                'thumb': it,
                'large': il,
            }

            items.append(item)

        msg = BaseMessage()
        msg.code = self.code
        msg.size = self.size
        msg.disposable = self.disposable
        msg.items = items
        msg.types = self.types
        msg.number_of_comments = self.number_of_comments
        msg.number_of_users = self.number_of_users
        msg.create_time = self.create_time.astimezone(pytz.UTC).isoformat()

        return msg.to_json()
