from validation import BaseForm
from wtforms import StringField
from wtforms.validators import Length, DataRequired


class ActivateForm(BaseForm):
    code = StringField(
        label='code',
        validators=[
            DataRequired(message='The code is required.'),
            Length(min=6, max=6, message='The code is invalid.'),
        ]
    )

    token = StringField(
        label='token',
        validators=[
            DataRequired(message='The token is required.'),
        ]
    )
