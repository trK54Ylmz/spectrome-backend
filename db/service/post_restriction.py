from db import get_session
from db.model import PostRestriction, User


class PostRestrictionService:
    def get_by_post_id(self, post_id):
        """
        Get post restrictions by post id

        :param int post_id: post identity
        :return: list of restrictions
        :rtype: list[db.model.User] or None
        """
        session = get_session()

        try:
            return session.query(User) \
                .join(PostRestriction, PostRestriction.user_id == User.uid) \
                .filter(PostRestriction.post_id == post_id) \
                .all()
        finally:
            session.close()

    def remove_by_post_id(self, post_id):
        """
        Remove post restrictions by given post id

        :param int post_id: the post identity
        """
        session = get_session()

        try:
            session.query(PostRestriction) \
                .filter(PostRestriction.post_id == post_id) \
                .delete()
            session.commit()
        finally:
            session.close()

    def create_all(self, restrictions):
        """
        Create all post restrictions

        :param list[db.model.PostRestriction] restrictions: list of restrictions
        """
        session = get_session()

        try:
            for r in restrictions:
                session.add(r)

            session.commit()
        except Exception as e:
            session.rollback()

            raise e
        finally:
            session.close()
