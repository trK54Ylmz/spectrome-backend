from boto3.session import Session
from util.config import config
from util.const import ScreenSize


class Process:
    def __init__(self, post_code, file, size, scale, session_code):
        self._post_code = post_code
        self._file = file
        self._size = size
        self._scale = scale
        self._session_code = session_code

        # create boto session
        session = Session()

        # create s3 client
        self._s3 = session.client(
            service_name='s3',
            aws_access_key_id=config.s3.access_key,
            aws_secret_access_key=config.s3.secret_key,
            endpoint_url='https://' + config.s3.host,
            region_name=config.s3.region,
        )

    def get_resize(self, width, height):
        """
        Get new width, new height, x offset and y offset of the file

        :param int width: width of the file
        :param int height: height of the file
        :return: new width, new height, x and y sizes
        :rtype: (int, int, int, int)
        """
        # get post resolution by post size type
        resolution = ScreenSize.from_type(self._size)

        width_rate = resolution[0] / width
        height_rate = resolution[1] / height

        # update screen scale according to selected screen size
        if self._scale == 1.0:
            resize = max(width_rate, height_rate)
            new_width = int(width * resize)
            new_height = int(height * resize)

            x = int((new_width - resolution[0]) / 2)
            y = int((new_height - resolution[1]) / 2)
        else:
            resize = max(width_rate, height_rate)
            new_width = int(width * resize * self._scale)
            new_height = int(height * resize * self._scale)

            x = int((new_width - resolution[0]) / 2)
            y = int((new_height - resolution[1]) / 2)

        return new_width, new_height, x, y

    def safety(self, path):
        """
        Check safety of files (video) or file (photo)
        """
        raise NotImplementedError

    def get_size(self):
        """
        Get width and height of the file
        """
        raise NotImplementedError

    def create(self):
        """
        Create new object by given object
        """
        raise NotImplementedError
