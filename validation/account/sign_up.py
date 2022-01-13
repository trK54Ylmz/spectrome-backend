from validation import BaseForm
from validation.custom import Ascii, Name, NotStart, Phone
from wtforms import StringField
from wtforms.validators import DataRequired, Email, Length


class SignUpForm(BaseForm):
    phone = StringField(
        label='phone',
        validators=[
            DataRequired(message='The phone number field is required.'),
            Phone(message='The phone number is invalid.')
        ]
    )

    email = StringField(
        label='email',
        validators=[
            DataRequired(message='The e-mail address field is required.'),
            Email(message='The e-mail address is invalid.')
        ]
    )

    username = StringField(
        label='username',
        validators=[
            DataRequired(message='The username field is required.'),
            Ascii(message='The username can contains a-z, 0-9 and dot.'),
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

    password = StringField(
        label='password',
        validators=[
            DataRequired(message='The password field is required.'),
            Length(
                min=6,
                max=150,
                message='The password field must be in 6-150 characters.',
            ),
        ]
    )

    name = StringField(
        label='name',
        validators=[
            DataRequired(message='The name field is required.'),
            Name(message='The name is invalid.'),
        ]
    )
