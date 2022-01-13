from db import get_session
from db.model import User
from sqlalchemy import or_


class UserService:
    def get_by_id(self, user_id):
        """
        Get user by user ID

        :param int user_id: user identifier
        :return: user instance
        :rtype: db.model.User or None
        """
        session = get_session()

        try:
            return session.query(User) \
                .filter(User.uid == user_id) \
                .first()
        finally:
            session.close()

    def get_by_username(self, username):
        """
        Get user by username

        :param str username: unique username
        :return: user instance
        :rtype: db.model.User or None
        """
        session = get_session()

        try:
            return session.query(User) \
                .filter(User.username == username) \
                .first()
        finally:
            session.close()

    def get_by_email_or_username(self, email, username):
        """
        Get by login ID which means username or e-mail address

        :param str email: e-mail address
        :param str username: username
        :return: user instance
        :rtype: User or None
        """
        session = get_session()

        # get by e-mail address or username
        f = or_(
            User.email == email,
            User.username == username,
        )

        try:
            return session.query(User).filter(f).first()
        finally:
            session.close()

    def get_by_code(self, code):
        """
        Get user by activation code

        :param str code: activation code
        :return: user instance
        :rtype: User or None
        """
        session = get_session()

        try:
            return session.query(User) \
                .filter(User.code == code) \
                .first()
        finally:
            session.close()

    def get_by_email(self, email):
        """
        Get user by e-mail address

        :param str email: e-mail address
        :return: user instance
        :rtype: User or None
        """
        session = get_session()

        try:
            return session.query(User) \
                .filter(User.email == email) \
                .first()
        finally:
            session.close()

    def create(self, user):
        """
        Create new user on the database

        :param User user: user instance
        """
        session = get_session()

        try:
            session.add(user)
            session.commit()
            session.refresh(user)
        finally:
            session.close()

    def update(self, user):
        """
        Update user instance

        :param User user: user instance
        """
        session = get_session()
        try:
            session.merge(user)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
