import json
import subprocess
from util import logger
from util.config import config


class FFmpeg:
    video = 1

    audio = 2

    def __init__(self):
        self.filters = []
        self.maps = []
        self.args = []
        self._vc = 0
        self._ac = 0
        self._fc = 0

    def probe(self, path):
        """
        Run ffmpeg probe based on selected file path

        :param str path: file location
        :return: details as JSON
        :rtype: dict
        """
        args = [
            'ffprobe', '-show_format', '-show_streams', '-print_format',
            'json', '-loglevel', 'quiet', path,
        ]

        # run process
        r = subprocess.run(args, capture_output=True)

        if len(r.stderr):
            raise Exception(r.stderr)
        return json.loads(r.stdout)

    def input(self, path):
        """
        Select input stream path

        :param str path: file location
        """
        self.input = path

    def filter(self, name, **kwargs):
        """
        Add ffmpeg filters to the selected streams

        :param str name: filter name
        :param dict[str, str] kwargs: custom filter parameters
        """
        t = None
        if 'type' in kwargs.keys():
            t = kwargs['type']
            del kwargs['type']

        f = {
            'name': name,
            'type': t,
            'args': kwargs,
        }

        self.filters.append(f)

    def output(self, path, **kwargs):
        """
        Select output path for the final stream

        :param str path: file location
        :param dict[str, str] kwargs: custom ffmpeg parameters
        """
        self.output = path
        self.args = kwargs

    def _filter(self):
        """
        Run default filter

        :return: ffmpeg filter
        :rtype: list[str]
        """
        filters = []
        i = 0
        for f in self.filters:
            if f['type'] is None:
                ft = ''
                if i == 0:
                    ft += '[0]'
                else:
                    ft += f'[s{i - 1}]'
                ft += f['name'] + '='

                args = []
                for k, v in f['args'].items():
                    args.append(f'{k}={v}')
                ft += ':'.join(args)
                ft += f'[s{i}]'
                filters.append(ft)
                i += 1
            elif i > 0 and f['type'] is not None:
                raise Exception('Invalid filter type.')

        if i > 0:
            self.maps.append(f'[s{i - 1}]')

        return filters

    def _video_filter(self):
        """
        Create video filter

        :return: ffmpeg video filter
        :rtype: list[str]
        """
        vf = []
        filters = []
        i = 0
        for f in self.filters:
            if f['type'] == self.video:
                ft = ''
                if i == 0:
                    ft += '[0:v]'
                else:
                    ft += f'[s{i - 1}]'
                ft += f['name'] + '='

                args = []
                for k, v in f['args'].items():
                    args.append(f'{k}={v}')
                ft += ':'.join(args)
                ft += f'[s{i}]'
                vf.append(ft)
                i += 1

        # update video filter counter
        self._vc = i

        if self._vc > 0:
            self.maps.append(f'[s{self._vc - 1}]')
            filters.append(';'.join(vf))

        return filters

    def _audio_filter(self):
        """
        Create audio filter

        :return: ffmpeg audio filter
        :rtype: list[str]
        """
        af = []
        filters = []
        i = 0
        for f in self.filters:
            if f['type'] == self.audio:
                ft = ''
                if i == 0:
                    ft += '[0:a]'
                else:
                    ft += f'[s{self._vc + i - 1}]'
                ft += f['name'] + '='

                args = []
                for k, v in f['args'].items():
                    args.append(f'{k}={v}')
                ft += ':'.join(args)
                ft += f'[s{self._vc + i}]'
                af.append(ft)
                i += 1

        # update audio filter counter
        self._ac = i

        if self._ac > 0:
            self.maps.append(f'[s{self._vc + i - 1}]')
            filters.append(';'.join(af))

        return filters

    def compile(self):
        """
        Compile command line ffmpeg arguments

        :return: command line parameters
        :rtype: list[str]
        """
        if self.input is None:
            raise Exception('The input is required.')
        if self.output is None:
            raise Exception('The output is required.')

        filters = []

        # run default filters
        df = self._filter()
        filters.extend(df)

        # run video filters
        df = self._video_filter()
        filters.extend(df)

        # run audio filters
        df = self._audio_filter()
        filters.extend(df)

        args = ['ffmpeg', '-i', self.input, '-v', '16']

        # add filters as parameter in ffmpeg
        if len(filters) > 0:
            args.extend(['-filter_complex', ';'.join(filters)])

        if len(self.maps) > 0:
            for m in self.maps:
                args.append('-map')
                args.append(m)

        if len(self.args.keys()) > 0:
            for k, v in self.args.items():
                args.append('-' + k)
                args.append(str(v))

        args.append(self.output)

        if config.app.debug:
            cmd = ' '.join(args)
            logger.info(f'Command is "{cmd}".')

        return args

    def run(self):
        """
        Run ffmpeg command

        :rtype: stdout and stderr outputs
        :rtype: tuple(str, str)
        """
        args = self.compile()

        if config.app.debug:
            logger.info(' '.join(args))

        # run process
        r = subprocess.run(args, capture_output=True)

        return r.stdout, r.stderr
