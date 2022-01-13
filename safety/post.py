import requests as r
from attrdict import AttrDict
from io import BytesIO
from util.config import config


class PostSafety:
    def check(self, session_code, items):
        """
        Check the safety of files

        :param str session_code: authorization code
        :param list[str] items: list of files
        :return: status of items
        :rtype: list[bool]
        """
        url = f'https://{config.safety.domain}/safety/post'

        files = dict()
        for i in range(len(items)):
            with open(items[i], 'rb') as f:
                files[f'files-{i}'] = BytesIO(f.read())

        headers = {'x-authorization': session_code}

        verify = not config.app.debug
        cert = (config.safety.public, config.safety.private)

        # send request to server
        res = r.post(url, verify=verify, files=files,  headers=headers, cert=cert)

        if res.status_code < 200 or res.status_code >= 300:
            raise Exception('Invalid status from safety check.')

        content = AttrDict(res.json())
        if not content.status:
            raise Exception(content.message)

        return list(map(lambda s: s == 1, content.safe))
