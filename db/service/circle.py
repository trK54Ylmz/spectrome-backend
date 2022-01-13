from db import get_session
from db.model import Circle, User


class CircleService:
    def get_by_from_to(self, from_id, to_id):
        """
        Get circle (from_id) according to given user id (to_id)

        :param int from_id: circle id
        :param int to_id: circle id
        :return: circle instance
        :rtype: db.model.Circle or None
        """
        session = get_session()

        try:
            return session.query(Circle) \
                .filter(Circle.from_id == from_id) \
                .filter(Circle.to_id == to_id) \
                .first()
        finally:
            session.close()

    def get_all(self, user_id, timestamp):
        """
        Get list circles according to given user id

        :param int user_id: circle id
        :param datetime.datetime timestamp: create time filter
        :return: list circle instance
        :rtype: list[db.model.Circle] or None
        """
        session = get_session()

        try:
            return session.query(User) \
                .select_from(Circle) \
                .join(User, User.uid == Circle.from_id) \
                .filter(Circle.to_id == user_id) \
                .filter(Circle.create_time < timestamp) \
                .limit(10) \
                .all()
        finally:
            session.close()

    def create(self, circle):
        """
        Create new circle between users

        :param db.model.Circle circle: circle instance
        """
        session = get_session()

        try:
            session.add(circle)
            session.commit()
            session.refresh(circle)
        finally:
            session.close()

    def remove(self, circle):
        """
        Remove circle from the database

        :param db.model.Circle circle: circle instance
        """
        session = get_session()

        try:
            session.delete(circle)
            session.commit()
        finally:
            session.close()
