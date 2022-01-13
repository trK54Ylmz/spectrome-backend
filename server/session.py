import pytz
from attrdict import AttrDict
from datetime import datetime
from flask import request
from redis import Redis
from util.config import config
from util.hash import Hash

redis = Redis(
    host=config.session.host,
    port=config.session.port,
    db=config.session.db
)


class Session:
    @staticmethod
    def exists(session_code):
        """
        Check user session

        :param str session_code: session key
        :return: existence of session
        :rtype: bool
        """
        return redis.get(f'ss.{session_code}') is not None

    @staticmethod
    def get(key=None):
        """
        Get session object

        :param str or None key: session key
        :return: session object
        :rtype: object
        """
        session_code = key or request.headers.get('x-authorization')

        data = redis.get(f'ss.{session_code}')
        if data is None:
            return None

        dc = Hash.decrypt(data)

        return AttrDict(dc)

    @staticmethod
    def get_tokens(user_id):
        """
        Get notification tokens by user id

        :param int user_id: user identity
        :return: list of tokens
        :rtype: list[str]
        """
        user_code = Hash.md5(str(user_id))

        members = redis.smembers(f'nt.{user_code}')
        if len(members) == 0:
            return None

        tokens = []
        for member in members:
            parts = member.decode('utf-8').split(':', 2)

            if len(parts) < 3:
                continue

            # token data
            token = parts[2]

            # populate tokens
            tokens.append(token)

        return tokens if len(tokens) > 0 else None

    @staticmethod
    def set_token(user_id, token):
        """
        Set notication token

        :param int user_id: user identity
        :param str token: notification token
        """
        user_code = Hash.md5(str(user_id))
        session_code = request.headers.get('x-authorization')
        now = str(int(datetime.now(tz=pytz.UTC).timestamp()))

        # redis member value
        member = f'{now}:{session_code}:{token}'

        members = redis.smembers(f'nt.{user_code}')
        if len(members) > 0:
            now = datetime.now(tz=pytz.UTC)

            # iterate over members and delete if member TTL expired
            for member in members:
                parts = member.decode('utf-8').split(':', 2)

                ttl = datetime.fromtimestamp(int(parts[0]), tz=pytz.UTC)

                # remove member if member TTL expired
                if (now - ttl).days > 10:
                    redis.srem(f'nt.{user_code}', member)

        # add new token
        redis.sadd(f'nt.{user_code}', member)

    @staticmethod
    def create(user):
        """
        Create new session for 1 hour

        :param db.model.User user: user object
        :return: session key
        :rtype: str
        """
        # generate session key
        tm = datetime.now(tz=pytz.UTC).isoformat()
        session_code = Hash.md5(f'{user.uid}.{tm}')
        session_key = f'ss.{session_code}'

        # generate refresh token
        token_code = f'st.{session_code}'

        data = dict()
        data['user_id'] = user.uid
        data['email'] = user.email
        data['username'] = user.username

        # encrypt session content
        session_data = Hash.encrypt(data)

        data = dict()
        data['user_id'] = user.uid

        # encrypt token data
        token_data = Hash.encrypt(data)

        # one month ttl
        ttl = 60 * 60 * 24 * 30

        # create refresh token and session on Redis
        redis.set(token_code, token_data, ex=ttl)
        redis.set(session_key, session_data, ex=ttl)

        return session_code

    @staticmethod
    def refresh(session_code):
        """
        Add extra time to key

        :param str session_code: redis key
        """
        # one month ttl
        ttl = 60 * 60 * 24 * 30

        redis.expire(f'ss.{session_code}', ttl)

    @staticmethod
    def remove(user_id):
        """
        Remove session key and session token key

        :param int user_id: user identity
        """
        session_code = request.headers.get('x-authorization')
        session_key = f'ss.{session_code}'
        token_key = f'st.{session_code}'

        # remove session
        redis.delete(session_key)
        redis.delete(token_key)

        user_code = Hash.md5(str(user_id))

        # get notification tokens
        members = redis.smembers(f'nt.{user_code}')
        if len(members) > 0:
            for member in members:
                parts = member.decode('utf-8').split(':', 2)

                # remove member
                if session_code == parts[1]:
                    redis.srem(f'nt.{user_code}', member)
