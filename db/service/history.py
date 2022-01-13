from db import get_session
from db.model import History, Post, User
from sqlalchemy import func
from sqlalchemy.sql.expression import desc


class HistoryService:
    def get_by_user(self, user_id, timestamp):
        """
        Get list of history by user id

        :param int user_id: user identity
        :param datetime.datetime timestamp: last query create time
        :return: list of histories
        :rtype: list[db.model.History] or None
        """
        session = get_session()

        pb = History.post_id
        ob = desc(History.create_time)

        sub_columns = [
            History.post_id,
            History.post_id,
            History.user_id,
            History.create_time,
            func.row_number().over(partition_by=pb, order_by=ob).label('row_number'),
        ]

        sub_query = session.query(*sub_columns) \
            .select_from(History) \
            .filter(History.create_time < timestamp) \
            .filter(History.user_id != user_id) \
            .filter(History.user_ids.contains([user_id])) \
            .subquery()

        columns = [
            User.username,
            Post.pid,
            Post.user_id,
            Post.code,
            Post.disposable,
            Post.size,
            Post.items,
            Post.types,
            Post.number_of_comments,
            Post.number_of_users,
            Post.create_time,
        ]

        try:
            return session.query(*columns) \
                .select_from(sub_query) \
                .join(Post, Post.pid == sub_query.c.post_id) \
                .join(User, User.uid == sub_query.c.user_id) \
                .filter(sub_query.c.row_number == 1) \
                .order_by(desc(Post.create_time)) \
                .limit(10) \
                .all()
        finally:
            session.close()

    def create(self, history):
        """
        Create new history on the database

        :param db.model.History history: history instance
        """
        session = get_session()

        try:
            session.add(history)
            session.commit()
            session.refresh(history)
        finally:
            session.close()

    def update(self, history):
        """
        Update history instance

        :param db.model.History history: history instance
        """
        session = get_session()
        try:
            session.merge(history)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
