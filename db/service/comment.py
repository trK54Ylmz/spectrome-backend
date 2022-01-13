from db import get_session
from db.model import Comment, User
from sqlalchemy import false, true


class CommentService:
    def get_by_id(self, comment_id):
        """
        Get comment by comment id

        :param int comment_id: comment identity
        :return: comment instance
        :rtype: db.model.Comment or None
        """
        session = get_session()

        try:
            return session.query(Comment) \
                .filter(Comment.cid == comment_id) \
                .first()
        finally:
            session.close()

    def get_owned_by_post_id(self, post_id):
        """
        Get owned comment by post id

        :param int post_id: post identity
        :return: comment instance
        :rtype: db.model.Comment or None
        """
        session = get_session()

        try:
            return session.query(Comment) \
                .filter(Comment.post_id == post_id) \
                .filter(Comment.owned == true()) \
                .first()
        finally:
            session.close()

    def get_by_post_id(self, post_id):
        """
        Get list of comments by post id

        :param int post_id: post identity
        :return: comment instance
        :rtype: list[db.model.Comment] or None
        """
        session = get_session()

        try:
            return session.query(Comment) \
                .filter(Comment.post_id == post_id) \
                .filter(Comment.owned == false()) \
                .order_by(Comment.create_time.desc()) \
                .all()
        finally:
            session.close()

    def get_history(self, post_id, timestamp):
        """
        Get comment history by post id and create time

        :param int post_id: post primary key
        :param datetime.datetime timestamp: last timestamp of the comment
        :return: list of comment instances
        :rtype: list[db.model.Comment] or None
        """
        session = get_session()

        c = [
            User.username,
            User.name,
            User.token,
            User.number_of_posts,
            User.number_of_circles,
            Comment.cid,
            Comment.code,
            Comment.message,
            Comment.create_time,
        ]

        try:
            return session.query(*c) \
                .join(Comment, Comment.user_id == User.uid) \
                .filter(Comment.post_id == post_id) \
                .filter(Comment.create_time < timestamp) \
                .order_by(Comment.create_time.desc()) \
                .limit(10) \
                .all()
        finally:
            session.close()

    def get_recent(self, post_id):
        """
        Get recent comments by post id and create time

        :param int post_id: post primary key
        :return: list of comment instances
        :rtype: list[db.model.Comment] or None
        """
        session = get_session()

        c = [
            User.username,
            User.name,
            User.token,
            User.number_of_posts,
            User.number_of_circles,
            Comment.cid,
            Comment.code,
            Comment.message,
            Comment.create_time,
        ]

        try:
            return session.query(*c) \
                .join(Comment, Comment.user_id == User.uid) \
                .filter(Comment.owned == false()) \
                .filter(Comment.post_id == post_id) \
                .order_by(Comment.create_time.desc()) \
                .limit(2) \
                .all()
        finally:
            session.close()

    def remove_by_post_id(self, post_id):
        """
        Remove comments by given post id

        :param int post_id: the post identity
        """
        session = get_session()

        try:
            session.query(Comment) \
                .filter(Comment.post_id == post_id) \
                .delete()
            session.commit()
        finally:
            session.close()

    def create(self, comment):
        """
        Create new comment on the database

        :param db.model.Comment comment: comment instance
        """
        session = get_session()

        try:
            session.add(comment)
            session.commit()
            session.refresh(comment)
        finally:
            session.close()
