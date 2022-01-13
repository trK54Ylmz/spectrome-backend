from validation import BaseForm
from validation.custom import Ascii, AtLeast
from wtforms import StringField
from wtforms.validators import DataRequired, Email, Length


class SignInForm(BaseForm):
    login_id = StringField(
        label='login_id',
        validators=[
            DataRequired(
                message='The e-mail address or username field is required.'
            ),
            AtLeast(
                validations=[
                    Ascii(
                        message='The username is invalid. Only a-z, 0-9 and . accepted.'
                    ),
                    Email(message='The e-mail address is invalid.'),
                ],
            ),
            Length(
                min=6,
                max=150,
                message='The e-mail or username field must be in 6-150 characters.',
            ),
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
