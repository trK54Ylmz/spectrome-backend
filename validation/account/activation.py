from validation import BaseForm
from wtforms import StringField
from wtforms.validators import DataRequired


class ActivationForm(BaseForm):
    token = StringField(
        label='token',
        validators=[
            DataRequired(message='The token is required.'),
        ]
    )
