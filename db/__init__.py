from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from util import Strings
from util.config import config


def get_engine():
    """
    Get SQLAlchemy engine by using configuration parameter

    :return: SQLAlchemy engine
    :rtype: sqlalchemy.engine.Engine
    """
    host = config.db.host
    port = config.db.port
    user = config.db.user
    password = config.db.password
    db = config.db.db

    u = f'postgresql://{user}:{password}@{host}:{port}/{db}'

    if Strings.is_empty(user) and Strings.is_empty(password):
        u = f'postgresql://{host}:{port}/{db}'

    u += '?client_encoding=utf8&sslmode=disable'

    pool_size = config.db.pool_size if config.db.pool_size is not None else 10
    extras = {
        'echo': config.app.debug,
        'echo_pool': config.app.debug,
        'pool_size': pool_size,
        'max_overflow': pool_size * 2,
    }

    return create_engine(u, **extras)


def get_session():
    """
    Returns SQLAlchemy session

    :return: session
    :rtype: sqlalchemy.orm.session.Session
    """
    return SessionItem()


# get default engine from db configuration
engine = get_engine()

Base = declarative_base()
SessionItem = sessionmaker(bind=engine, autocommit=False)
