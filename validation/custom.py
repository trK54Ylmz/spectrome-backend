import phonenumbers
import re
from phonenumbers.phonenumberutil import NumberParseException
from wtforms.validators import ValidationError


class Ascii:
    def __init__(self, message):
        """
        Validate input that if acceptable ascii format

        :param str message: validation error message
        """
        self._message = message

    def __call__(self, form, field):
        if not re.match(r'^[a-z0-9\.]+$', field.data):
            raise ValidationError(self._message)


class AtLeast:
    def __init__(self, validations):
        """
        At least one of the validations must be valid

        :param list[object] validations: validation group
        """
        self._validations = validations

    def __call__(self, form, field):
        msg = None
        for v in self._validations:
            try:
                v.__call__(form, field)

                # break if validation is valid
                return
            except ValidationError as e:
                if msg is None:
                    msg = e.args[0]

        raise ValidationError(msg)


class Name:
    def __init__(self, message):
        """
        Validate person name

        :param str message: validation error message
        """
        self._message = message

    def __call__(self, form, field):
        n = r'([\.\-\']{1}|[a-zA-Z]|[À-Ö]|[Ø-ö]|[ø-ǿ]|[Ȁ-ʯ]|[Ḁ-ỿ])'

        regex = r'^' + n + r'{1,30}[\s]{1}' + n + r'{0,30}[\s]{0,1}' + n + r'{1,30}$'
        if not re.match(regex, field.data, re.UNICODE):
            raise ValidationError(self._message)


class NotStart:
    def __init__(self, text, message):
        """
        Validate input does not starts with given text

        :param str text: text that input should not starts
        :param str message: validation error message
        """
        self._text = text
        self._message = message

    def __call__(self, form, field):
        if field.data is not None and field.data.startswith(self._text):
            raise ValidationError(self._message)


class Phone:
    def __init__(self, message):
        """
        Validate phone number

        :param str message: validation error message
        """
        self._message = message

    def __call__(self, form, field):
        if field.data is not None:
            if not field.data.startswith('+'):
                raise ValidationError(self._message)

            try:
                # parse phone number
                n = phonenumbers.parse(field.data, None)

                if not phonenumbers.is_valid_number(n):
                    raise ValidationError(self._message)
            except NumberParseException:
                raise ValidationError(self._message)


class Unique:
    def __init__(self, message):
        """
        Validate that items must be unique

        :param str message: validation error message
        """
        self._message = message

    def __call__(self, form, field):
        expected = set(field.data)
        got = list(field.data)

        if field.data is not None and len(expected) != len(got):
            raise ValidationError(self._message)
