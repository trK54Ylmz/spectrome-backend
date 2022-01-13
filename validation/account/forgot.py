from validation import BaseForm
from validation.custom import Ascii, NotStart, Phone
from wtforms import StringField
from wtforms.validators import DataRequired, Length


class ForgotForm(BaseForm):
    phone = StringField(
        label='phone',
        validators=[
            DataRequired(message='The phone number field is required.'),
            Phone(message='The phone number is invalid.')
        ]
    )

    username = StringField(
        label='username',
        validators=[
            DataRequired(message='The username field is required.'),
            Ascii(message='The username is invalid.'),
            Length(
                min=2,
                max=24,
                message='The username must be in 2-24 characters.',
            ),
            NotStart(
                text='.',
                message='The username cannot starts with "." character'
            )
        ]
    )
