import io
import re
import os
from server import app
from botocore.exceptions import ClientError
from boto3.session import Session
from flask import Blueprint, request, send_file, stream_with_context, Response
from util.config import config
from validation.cdn import ProfileForm, PostItemForm
from werkzeug.datastructures import Headers, MultiDict


# create boto session
session = Session()

# create s3 client
s3 = session.client(
    service_name='s3',
    aws_access_key_id=config.s3.access_key,
    aws_secret_access_key=config.s3.secret_key,
    endpoint_url='https://' + config.s3.host,
    region_name=config.s3.region,
)

cdn = Blueprint('cdn', app.name)


@cdn.route('/profile/<code>/<size>.jpg', methods=['GET'])
def profile(code, size):
    """
    Get profile photo

    :param str code: profile photo code
    :param int size: profile photo size
    """
    path = os.getcwd() + '/site/images/'

    # create form arguments
    args = MultiDict()
    args.add('code', code)
    args.add('size', size)

    form = ProfileForm(args)

    # validate form
    if not form.validate():
        return form.error()

    bucket = config.profile.bucket
    folder = config.profile.folder
    object_name = f'{folder}/{code}.{size}.jpg'

    # get object from object storage
    try:
        o = s3.get_object(Bucket=bucket, Key=object_name)

        b = io.BytesIO(o.get('Body').read())
        return send_file(b, mimetype='image/jpeg')
    except ClientError:
        with open(path + f'default.{size}.jpg', 'rb') as f:
            b = io.BytesIO(f.read())
            return send_file(b, mimetype='image/jpeg')


@cdn.route('/post/<code>/<hashes>.<size>.<extension>', methods=['GET'])
def post(code, hashes, size, extension):
    """
    Get post photo or video

    :param str code: unique post code
    :param str hash: unicode post item hash
    :param str size: post item size. "thumb" or "large" supported
    :param str extension: post item file extension
    """
    args = MultiDict()
    args.add('code', code)
    args.add('hashes', hashes)
    args.add('size', size)
    args.add('extension', extension)

    form = PostItemForm(args)

    # validate form
    if not form.validate():
        return form.error()

    bucket = config.share.bucket
    folder = config.share.folder
    object_name = f'{folder}/{code}/{hashes}.{size}.{extension}'

    # get object from object storage
    try:
        # get object from S3
        o = s3.get_object(Bucket=bucket, Key=object_name)

        if extension.lower() == 'jpg':
            # read bytes of image file
            b = io.BytesIO(o.get('Body').read())

            return send_file(b, mimetype='image/jpeg')

        # check if range header is active
        range_header = request.headers.get('Range', None)

        if range_header:
            g = re.search(r'(\d+)-(\d*)', range_header).groups()

            if len(g) == 2 and g[0].isdigit() and g[1].isdigit():
                start = int(g[0])
                end = int(g[1])

                headers = Headers()

                if end > start:
                    length = o['ContentLength']

                    ranges = f'bytes={start}-{end}'

                    # get object from S3 by using range
                    o = s3.get_object(Bucket=bucket, Key=object_name, Range=ranges)

                    # set partial response headers
                    headers.add('content-range', f'bytes {start}-{end}/{length}')
                    headers.add('accept-ranges', 'bytes')
                    headers.add('content-transfer-encoding', 'binary')
                    headers.add('connection', 'keep-alive')
                    headers.add('content-Type', 'video/mp4')
                    if end == 1:
                        headers.add('content-length', '1')
                    else:
                        headers.add('content-length', o['ContentLength'])

                    sc = stream_with_context(o.get('Body').iter_chunks())

                    return Response(
                        response=sc,
                        mimetype='video/mp4',
                        content_type='video/mp4',
                        headers=headers,
                        status=206,
                        direct_passthrough=True,
                    )

        sc = stream_with_context(o.get('Body').iter_chunks())

        return Response(response=sc, mimetype='video/mp4')
    except ClientError:
        return 'The key does not exists.'
