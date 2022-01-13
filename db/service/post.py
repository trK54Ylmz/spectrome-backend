from db import get_session
from db.model import Post, PostRestriction, PostStatus, User
from sqlalchemy import and_, true
from sqlalchemy.orm import aliased


class PostService:
    def get_by_code(self, code):
        """
        Get post by code

        :param str code: post code
        :return: post instance
        :rtype: db.model.Post or None
        """
        session = get_session()

        try:
            return session.query(Post).filter(Post.code == code).first()
        finally:
            session.close()

    def get_waterfall(self, user_id, timestamp):
        """
        Get waterfall posts

        :param int user_id: user primary key
        :param datetime.datetime timestamp: last timestamp of the post
        :return: list of post instance
        :rtype: list[db.model.Post] or None
        """
        session = get_session()

        f = [
            Post.status == PostStatus.ACTIVATED,
            Post.create_time < timestamp,
        ]

        # my posts filter
        mpf = [
            Post.user_id == user_id,
        ]

        my_posts = session.query(Post) \
            .filter(*(mpf + f)) \
            .order_by(Post.create_time.desc())\
            .limit(10)

        # post restriction user id
        fpf = [
            PostRestriction.user_id == user_id,
        ]

        circle_posts = session.query(Post) \
            .join(PostRestriction, PostRestriction.post_id == Post.pid) \
            .filter(*(fpf + f)) \
            .order_by(Post.create_time.desc()) \
            .limit(10)

        # define post query as subquery
        ps = my_posts.union(circle_posts).subquery()

        # use subquery as alias
        p = aliased(Post, alias=ps, adapt_on_names=True)

        c = [
            User.username,
            User.name,
            User.token,
            User.number_of_posts,
            User.number_of_circles,
            p.pid,
            p.user_id,
            p.code,
            p.disposable,
            p.size,
            p.items,
            p.types,
            p.number_of_comments,
            p.number_of_users,
            p.create_time,
        ]

        try:
            return session.query(*c) \
                .join(p, User.uid == p.user_id)\
                .order_by(p.create_time.desc()) \
                .limit(10) \
                .all()
        finally:
            session.close()

    def get_by_from_to(self, from_id, to_id, timestamp):
        """
        Get circle user posts

        :param int from_id: circle user id
        :param int to_id: circle user id
        :param datetime.datetime timestamp: last timestamp of the post
        :return: list of post instance
        :rtype: list[db.model.Post] or None
        """
        session = get_session()

        f = [
            Post.user_id == to_id,
            Post.status == PostStatus.ACTIVATED,
            Post.create_time < timestamp,
            PostRestriction.rid.isnot(None),

        ]

        j = [
            PostRestriction.post_id == Post.pid,
            PostRestriction.user_id == from_id,
        ]

        try:
            return session.query(Post) \
                .outerjoin(PostRestriction, and_(*j)) \
                .filter(*f) \
                .order_by(Post.create_time.desc()) \
                .limit(10) \
                .all()
        finally:
            session.close()

    def get_disposables(self, timestamp):
        """
        Get list of disposable posts that need to be removed

        :param datetime.datetime timestamp: last timestamp of the post
        :return: list of post instance
        :rtype: list[db.model.Post] or None
        """
        session = get_session()

        f = [
            Post.disposable == true(),
            Post.status == PostStatus.ACTIVATED,
            Post.create_time < timestamp,
        ]

        try:
            return session.query(Post) \
                .filter(*f) \
                .order_by(Post.create_time.asc()) \
                .limit(10) \
                .all()
        finally:
            session.close()

    def get_all(self, user_id, timestamp):
        """
        Get all posts by timestamp iterator

        :param int user_id: user primary key
        :param datetime.datetime timestamp: last timestamp of the post
        :return: list of post instance
        :rtype: list[db.model.Post] or None
        """
        session = get_session()

        f = [
            Post.user_id == user_id,
            Post.status == PostStatus.ACTIVATED,
            Post.create_time < timestamp,
        ]

        try:
            return session.query(Post) \
                .filter(*f) \
                .order_by(Post.create_time.desc())\
                .limit(10) \
                .all()
        finally:
            session.close()

    def delete_all(self, posts):
        """
        Remove posts by given list of posts

        :param list[db.model.Post] posts: list of post instances
        """
        session = get_session()

        try:
            for post in posts:
                session.delete(post)
            session.commit()
        finally:
            session.close()

    def create(self, post):
        """
        Create new post on the database

        :param db.model.Post post: post instance
        """
        session = get_session()

        try:
            session.add(post)
            session.commit()
            session.refresh(post)
        finally:
            session.close()

    def update(self, post):
        """
        Update post instance

        :param db.model.Post post: post instance
        """
        session = get_session()
        try:
            session.merge(post)
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
