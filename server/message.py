import json
from flask import Response


class BaseMessage:
    def __init__(self, **kwargs):
        """
        Create empty base message
        """
        for k, v in kwargs.items():
            self.__dict__[k] = v

    def __setattr__(self, key, value):
        """
        Add or update key

        :param str key: object key name
        :param str or float or int value: object value
        """
        self.__dict__[key] = value

    def to_json(self):
        """
        Return object as json

        :rtype: dict
        """
        return self.__dict__


class Message:
    def __init__(self, message=None, status=False, **kwargs):
        """
        Create message response object

        :param str or None message: response error etc. message
        :param bool or None status: response status
        :param dict or None kwargs: extra params for response
        """
        self.status = status
        self.message = message

        for k, v in kwargs.items():
            self.__dict__[k] = v

    def __setattr__(self, key, value):
        """
        Add or update key

        :param str key: object key name
        :param str or float or int value: object value
        """
        self.__dict__[key] = value

    def json(self, status=200):
        """
        Encode response as json object

        :return: json response object
        :rtype: Response
        """
        o = self.__dict__
        if self.message is None:
            o.pop('message')

        # encode json object
        return Response(
            status=status,
            response=json.dumps(o, ensure_ascii=False),
            mimetype='application/json; charset=utf-8',
        )
