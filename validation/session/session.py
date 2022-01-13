from validation import BaseForm
from wtforms import StringField
from wtforms.validators import DataRequired, Length


class SessionForm(BaseForm):
    session = StringField(
        label='session',
        validators=[
            DataRequired(
                message='The session token is required.'
            ),
            Length(
                min=30,
                max=60,
                message='The session token is invalid.',
            ),
        ]
    )
