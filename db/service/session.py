from db import get_session
from db.model import SessionToken


class SessionTokenService:
    def get_by_token(self, token):
        """
        Get session token by token code

        :param str token: session token
        :return: session token instance
        :rtype: SessionToken or None
        """
        session = get_session()

        try:
            return session.query(SessionToken).filter(SessionToken.token == token).first()
        finally:
            session.close()

    def get_by_token_and_user_id(self, token, user_id):
        """
        Get session token by token code and user id

        :param str token: session token
        :param int user_id: user id
        :return: session token instance
        :rtype: SessionToken or None
        """
        session = get_session()

        try:
            return session.query(SessionToken) \
                .filter(SessionToken.token == token) \
                .filter(SessionToken.user_id == user_id) \
                .first()
        finally:
            session.close()

    def delete_by_user_id(self, user_id):
        """
        Delete all session tokens of the user

        :param int user_id: user id
        """
        session = get_session()

        try:
            session.query(SessionToken) \
                .filter(SessionToken.user_id == user_id) \
                .delete()
            session.commit()
        finally:
            session.close()

    def create(self, token):
        """
        Create new session token on the database

        :param SessionToken token: session token instance
        """
        session = get_session()

        try:
            session.add(token)
            session.commit()
        finally:
            session.close()
