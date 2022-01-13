import os
import shutil
from .base import Process
from datetime import datetime
from pathlib import Path
from post import FFmpeg
from random import randint
from safety import PostSafety
from util.config import config
from util.const import ScreenSize
from util.hash import Hash


class VideoProcess(Process):
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

        width = 0
        height = 0
        channels = 0

        # extract width and height from channels
        for stat in stats['streams']:
            if stat['codec_type'] == 'video':
                width = stat['width']
                height = stat['height']
            elif stat['codec_type'] == 'audio':
                channels = stat['channels']

        if width == 0 or height == 0:
            raise Exception('Video width and height could not extracted.')

        if channels == 0:
            raise Exception('Audio channel could not extracted.')

        return width, height

    def safety(self, file):
        """
        Check safety of the video

        :param str file: list of file locations
        :return: file is safe or not
        :rtype: bool
        """
        ps = PostSafety()

        unique = Hash.md5(datetime.now().isoformat() + str(randint(0, 1000)))
        output = f'/tmp/samples/{unique}/'

        # create temporary directory
        if not os.path.exists(output):
            os.mkdir(output)

        f = FFmpeg()
        f.input(self._file)
        f.output(output + 'sample-%d.jpg', vf='fps=1', pix_fmt='yuvj422p')

        out, err = f.run()

        if len(err) > 0:
            shutil.rmtree(output)
            raise Exception('The sample files could not be created.')

        items = []

        # populate safety check inputs
        for f in os.listdir(output):
            if not f.endswith('.jpg'):
                continue

            # populate with files
            items.append(output + '/' + f)

        stats = ps.check(session_code=self._session_code, items=items)

        # remote temporary directory
        shutil.rmtree(output)

        if len(stats) == 0:
            return False

        return False in stats

    def create(self):
        """
        Create and upload given video file according size and scale

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
            'crf': 18,
            'ac': 2,
            'vcodec': 'libx264',
            'acodec': 'aac',
            'preset': 'slow',
        }

        thumb_arguments = {
            'vframes': 1,
            'qscale:v': 10,
            'lossless': 0,
            'ss': '00:00:10.000',
        }

        # get new width, new height, x offset and y offset
        new_width, new_height, x, y = self.get_resize(width, height)

        # create large and thumbnail file output path
        large_path = f'{parent}/{name}.large.mp4'
        thumb_path = f'{parent}/{name}.thumb.jpg'

        bucket = config.share.bucket
        folder = config.share.folder

        f = FFmpeg()
        f.input(self._file)
        f.filter('scale', type=f.video, width=new_width, height=new_height)
        f.filter('crop', type=f.video, out_w=resolution[0], out_h=resolution[1], x=x, y=y)
        f.filter('volume', type=f.audio, volume=1)
        f.output(large_path, **arguments)

        # convert source file to our standarts
        out, err = f.run()

        if len(err) > 0:
            raise Exception(err)

        # check safety of file
        status = self.safety(large_path)

        if not status:
            raise Exception('File has NSFW content.')

        object_path = f'{folder}/{self._post_code}/{name}.large.mp4'

        # upload resized video to cloud storage
        self._s3.upload_file(large_path, bucket, object_path)

        f = FFmpeg()
        f.input(large_path)

        # crop thumbnail if video size is not square
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

        object_path = f'{folder}/{self._post_code}/{name}.thumb.jpg'
        self._s3.upload_file(large_path, bucket, object_path)

        return name
