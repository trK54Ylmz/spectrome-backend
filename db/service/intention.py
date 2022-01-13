from db import get_session
from db.model import Intention, User
from sqlalchemy import false


class IntentionService:
    def get_by_code(self, code):
        """
        Get circle intention by code

        :param str code: intention hash code
        :return: intention instance
        :rtype: db.model.Intention or None
        """
        session = get_session()

        try:
            return session.query(Intention) \
                .filter(Intention.code == code) \
                .first()
        finally:
            session.close()

    def get_by_from_to(self, from_id, to_id):
        """
        Get circle intention (to_id) according to given user id (from_id)

        :param int from_id: circle id
        :param int to_id: circle id
        :return: intention instance
        :rtype: db.model.Intention or None
        """
        session = get_session()

        try:
            return session.query(Intention) \
                .filter(Intention.from_id == from_id) \
                .filter(Intention.to_id == to_id) \
                .first()
        finally:
            session.close()

    def get_by_target_id(self, user_id):
        """
        Get circle intentions according to given user id

        :param int user_id: circle id
        :return: intention instance
        :rtype: list[db.model.Intention] or None
        """
        session = get_session()

        columns = [
            Intention.code,
            Intention.from_id,
            Intention.create_time,
            User.username,
            User.name,
            User.token,
        ]

        try:
            return session.query(*columns) \
                .join(User, User.uid == Intention.from_id) \
                .filter(Intention.to_id == user_id) \
                .order_by(Intention.create_time.desc()) \
                .limit(10) \
                .all()
        finally:
            session.close()

    def get_by_unsent(self, to_id, limit=10):
        """
        Get least recent unsent circle request

        :param int to_id: circle id
        :param int limit: number of records
        :return: intention instance
        :rtype: db.model.Intention or None
        """
        session = get_session()

        columns = [
            Intention.code,
            Intention.from_id,
            Intention.create_time,
            User.username,
            User.name,
            User.token,
        ]

        try:
            return session.query(*columns) \
                .join(User, User.uid == Intention.from_id) \
                .filter(Intention.to_id == to_id) \
                .filter(Intention.sent == false()) \
                .order_by(Intention.create_time.asc()) \
                .limit(limit) \
                .all()
        finally:
            session.close()

    def create(self, intention):
        """
        Create new intention on the database

        :param db.model.Intention intention: intention instance
        """
        session = get_session()

        try:
            session.add(intention)
            session.commit()
            session.refresh(intention)
        finally:
            session.close()

    def update(self, intention):
        """
        Update intention instance

        :param db.model.Intention intention: intention instance
        """
        session = get_session()
        try:
            session.merge(intention)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def remove(self, intention):
        """
        Remove intention from the database

        :param db.model.Intention intention: intention instance
        """
        session = get_session()

        try:
            session.delete(intention)
            session.commit()
        finally:
            session.close()
