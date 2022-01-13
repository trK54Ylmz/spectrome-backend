from .log import init_logging

# initialize logger
logger = init_logging('spectrome')


class Strings:
    @staticmethod
    def is_empty(text):
        """
        Check string is empty or not
        :param str text: the input string object
        :return: true if string is empty, false otherwise
        :rtype: bool
        """
        if text is None or type(text) != str:
            return True

        return len(text) == 0
