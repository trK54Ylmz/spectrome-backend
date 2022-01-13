from validation import BaseForm
from wtforms import StringField
from wtforms.validators import DataRequired, Optional


class ProfilePostForm(BaseForm):
    username = StringField(
        label='username',
        validators=[
            DataRequired(message='The username is required.'),
        ]
    )

    timestamp = StringField(
        label='timestamp',
        validators=[
            Optional(),
        ]
    )
