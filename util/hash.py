import json
import uuid
import zlib
from hashlib import md5


class Hash:
    @staticmethod
    def md5(text):
        """
        Generate md5 hash

        :param str text: plain-text input
        :return: hashed text
        :rtype: str
        """
        hasher = md5()
        hasher.update(text.encode('utf-8'))

        return hasher.hexdigest()

    @staticmethod
    def uuid():
        """
        Generate UUIDv4 hash

        :return: hashed text
        :rtype: str
        """
        return str(uuid.uuid4())

    @staticmethod
    def encrypt(obj):
        """
        Create hash text by using JSON and GZIP

        :param dict obj: dictionary input
        :return: hashed text as byte array
        :rtype: bytes
        """
        return zlib.compress(json.dumps(obj).encode('utf-8'))

    @staticmethod
    def decrypt(b):
        """
        Parse hash text

        :param bytes b: hashed text as byte array
        :return: generated input data
        :rtype: dict
        """
        return json.loads(zlib.decompress(b).decode('utf-8'))
