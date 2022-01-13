from validation import BaseForm
from wtforms import StringField
from wtforms.validators import DataRequired, Length


class ResetForm(BaseForm):
    code = StringField(
        label='code',
        validators=[
            DataRequired(message='The code field is required.'),
            Length(min=6, max=6, message='The code is invalid.'),
        ]
    )

    token = StringField(
        label='token',
        validators=[
            DataRequired(message='The token is required.'),
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
