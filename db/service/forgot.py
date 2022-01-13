from db import get_session
from db.model import Forgot


class ForgotService:
    def get_by_user_id(self, user_id):
        """
        Get forgot by forgot code

        :param int user_id: user primary key
        :return: forgot instance
        :rtype: db.model.Forgot or None
        """
        session = get_session()

        try:
            return session.query(Forgot) \
                .filter(Forgot.user_id == user_id) \
                .first()
        finally:
            session.close()

    def get_by_code(self, code):
        """
        Get forgot by forgot code

        :param str code: activation code
        :return: forgot instance
        :rtype: db.model.Forgot or None
        """
        session = get_session()

        try:
            return session.query(Forgot) \
                .filter(Forgot.code == code) \
                .first()
        finally:
            session.close()

    def create(self, forgot):
        """
        Create new forgot password on the database

        :param db.model.Forgot forgot: forgot instance
        """
        session = get_session()

        try:
            session.add(forgot)
            session.commit()
            session.refresh(forgot)
        finally:
            session.close()

    def remove(self, forgot):
        """
        Update forgot instance

        :param db.model.Forgot forgot: forgot instance
        """
        session = get_session()
        try:
            session.delete(forgot)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
