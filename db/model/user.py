from db import Base
from server.message import BaseMessage
from sqlalchemy import Column, Integer, String, SmallInteger, TIMESTAMP as Timestamp
from util.config import config


class UserStatus:
    CREATED = 1
    EXPIRED = 2
    ACTIVATION_WAIT = 3
    ACTIVATED = 4
    BANNED = 5
    DELETED = 6


class User(Base):
    __tablename__ = 'users'

    uid = Column('id', Integer, primary_key=True, autoincrement=True)
    username = Column('username', String(32), nullable=False, unique=True)
    email = Column('email', String(150), unique=True, nullable=False)
    name = Column('name', String(200), nullable=False)
    password = Column('password', String(500), nullable=False)
    phone = Column('phone', String(20), nullable=False)
    country = Column('country', String(2))
    language = Column('language', String(10))
    number_of_posts = Column('posts', Integer, default=0)
    number_of_circles = Column('circles', Integer, default=0)
    status = Column('status', SmallInteger, default=UserStatus.CREATED)
    code = Column('code', String(6), index=True)
    token = Column('token', String(64), index=True)
    create_time = Column('create_time', Timestamp(timezone=True), nullable=False)
    update_time = Column('update_time', Timestamp(timezone=True))
    last_login = Column('last_login', Timestamp(timezone=True))

    def to_json(self):
        """
        Return database instance as json object

        :return: json response as dictionary
        :rtype: dict
        """
        name = 'default' if self.token is None else self.token
        scheme = 'http' if config.app.debug else 'https'
        domain = config.app.cdn

        msg = BaseMessage()
        msg.username = self.username
        msg.name = self.name
        msg.photo_url = f'{scheme}://{domain}/profile/{name}/1.jpg'
        msg.posts = self.number_of_posts
        msg.circles = self.number_of_circles

        return msg.to_json()
