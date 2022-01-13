import pytz
from datetime import datetime, timedelta
from db.service import CommentService, PostRestrictionService, PostService
from task import celery


@celery.task(serializer='json')
def disposable_task():
    """
    Remove disposable posts
    """
    cs = CommentService()
    prs = PostRestrictionService()
    ps = PostService()

    dt = datetime.now(tz=pytz.UTC) - timedelta(days=1)

    while True:
        # get disposables
        posts = ps.get_disposables(timestamp=dt)

        if len(posts) == 0:
            return

        # update last create time as iterator time
        dt = posts[0].create_time

        # remove all posts to be need remove
        ps.delete_all(posts)

        for post in posts:
            # remove comments by post id
            cs.remove_by_post_id(post_id=post.pid)

            # remove post restriced users by post id
            prs.remove_by_post_id(post_id=post.pid)
