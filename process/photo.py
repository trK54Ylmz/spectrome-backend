import os
from .base import Process
from pathlib import Path
from post import FFmpeg
from safety import PostSafety
from util.config import config
from util.const import ScreenSize


class PhotoProcess(Process):
    def get_size(self):
        """
        Get width and height of the file

        :return: width and height
        :rtype: (int, int)
        """
        if not os.path.exists(self._file):
            raise Exception('File does not exists.')

        f = FFmpeg()

        # get stats
        stats = f.probe(self._file)

        width = stats['streams'][0]['width']
        height = stats['streams'][0]['height']

        return width, height

    def safety(self, file):
        """
        Check safety of the photo

        :param str file: list of file locations
        :return: file is safe or not
        :rtype: bool
        """
        ps = PostSafety()

        stats = ps.check(session_code=self._session_code, items=[file])

        if len(stats) == 0:
            return False

        return stats[0]

    def create(self):
        """
        Create and upload given image file according size and scale

        :return: unique id of the file
        :rtype: str
        """
        path = Path(self._file)

        # get parent directory location
        parent = str(path.parent)

        # get file name
        name = path.name.split('.')[0]

        width, height = self.get_size()

        # get post resolution by post size type
        resolution = ScreenSize.from_type(self._size)

        # ffmpeg output arguments
        arguments = {
            'qscale:v': 2,
            'compression_level': 5,
        }

        thumb_arguments = {
            'qscale:v': 10,
            'compression_level': 8,
        }

        # get new width, new height, x offset and y offset
        new_width, new_height, x, y = self.get_resize(width, height)

        # create large and thumbnail file output path
        large_path = f'{parent}/{name}.large.jpg'
        thumb_path = f'{parent}/{name}.thumb.jpg'

        bucket = config.share.bucket
        post_folder = config.share.folder

        f = FFmpeg()
        f.input(self._file)
        f.filter('scale', width=new_width, height=new_height)
        f.filter('crop', out_w=resolution[0], out_h=resolution[1], x=x, y=y)
        f.output(large_path, **arguments)

        # convert source file to our standarts
        out, err = f.run()

        if len(err) > 0:
            raise Exception(err)

        # check safety of file
        status = self.safety(large_path)

        if not status:
            raise Exception('File has NSFW content.')

        object_path = f'{post_folder}/{self._post_code}/{name}.large.jpg'

        # upload resized file to s3 bucket
        self._s3.upload_file(large_path, bucket, object_path)

        f = FFmpeg()
        f.input(large_path)

        # crop thumbnail if photo size is not square
        if ScreenSize.from_type(self._size) != ScreenSize.SQUARE:
            lowest = min(resolution[0], resolution[1])
            x = (resolution[0] - lowest) / 2
            y = (resolution[1] - lowest) / 2
            f.filter('crop', out_w=lowest, out_h=lowest, x=x, y=y)

        f.filter('scale', width=360, height=360)
        f.output(thumb_path, **thumb_arguments)

        # convert source file to thumbnail standarts
        out, err = f.run()

        if len(err) > 0:
            raise Exception(err)

        object_path = f'{post_folder}/{self._post_code}/{name}.thumb.jpg'

        # upload resized file to s3 bucket
        self._s3.upload_file(thumb_path, bucket, object_path)

        return name
