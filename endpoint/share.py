import os
import time
from db.model import PostType, PostStatus
from flask import Blueprint, request
from pathlib import Path
from server import app
from server.cache import redis
from server.message import Message
from server.session import Session
from task.share import create_post_task
from validation.share import PostUploadForm, PostStatusForm
from util.hash import Hash
from werkzeug.datastructures import MultiDict

share = Blueprint('share', app.name)


@share.route('/status/<code>', methods=['GET'])
def get_status(code):
    """
    Get status of upload operation

    :rtype: flask.Response
    """
    m = Message()

    # extend arguments
    args = MultiDict(request.args)
    args.add('code', code)

    form = PostStatusForm(args)

    # validate form
    if not form.validate():
        m.message = form.error()
        return m.json()

    # the post code does not exists
    if not redis.exists(f'ps.{code}'):
        return m.json()

    m.failed = False
    m.done = False

    # get post creation status
    status = int(redis.get(f'ps.{code}'))

    if status == PostStatus.UPLOADED:
        m.state = 'uploaded'
    elif status == PostStatus.PROCESSING:
        m.state = 'processing'
    elif status == PostStatus.CREATED:
        m.state = 'created'
    elif status == PostStatus.ACTIVATED:
        m.state = 'activated'
        m.done = True
    elif status == PostStatus.BANNED:
        m.state = 'banned'
        m.failed = True
        m.done = True
    elif status == PostStatus.DELETED:
        m.state = 'deleted'
        m.failed = True
        m.done = True

    m.status = True

    return m.json()


@share.route('/post', methods=['POST'])
def upload():
    """
    Create new post

    :rtype: flask.Response
    """
    m = Message()

    form = PostUploadForm()

    # validate form
    if not form.validate():
        m.message = form.error()
        return m.json()

    # restricted users should be selected
    if len(form.users.data) == 0:
        m.message = 'Please specify users to share.'
        return m.json()

    # number files scales and number of files must be equal
    if len(form.files) != len(form.scales):
        m.message = 'Invalid file selection.'
        return m.json()

    # number of file types and number of files must be equal
    if len(form.files) != len(form.types):
        m.message = 'Invalid file type selection.'
        return m.json()

    # create post code
    unique_id = Hash.uuid()
    tm = time.time()
    code = Hash.md5(f'{unique_id} - {tm}')

    # create status value
    redis.set(f'ps.{code}', str(PostStatus.UPLOADED), ex=60 * 60 * 1)

    # create temporary directory
    tmp_dir = Path(f'/tmp/source/{code}')
    if not tmp_dir.parent.exists():
        tmp_dir.parent.mkdir()
    if not tmp_dir.exists():
        tmp_dir.mkdir()

    abs_path = str(tmp_dir.absolute())

    files = []
    for i in range(len(form.files.data)):
        name = Hash.uuid()
        extension = 'jpg' if form.types[i].data == PostType.PHOTO else 'mp4'

        # create local path
        file_path = abs_path + os.path.sep + name + '.' + extension

        # populate local files
        files.append(file_path)

        # save file to the local temporary directory
        form.files[i].data.save(file_path)

    # get user id from session
    session = Session.get()

    # create post in the background
    create_post_task.delay(
        user_id=session.user_id,
        code=code,
        files=files,
        path=abs_path,
        size=form.size.data,
        types=form.types.data,
        scales=form.scales.data,
        users=form.users.data,
        message=form.message.data,
        disposable=form.disposable.data,
        session_code=request.headers.get('x-authorization'),
    )

    # return post code
    m.code = code
    m.status = True

    return m.json()
