from validation import BaseForm
from wtforms import StringField
from wtforms.validators import DataRequired


class NotificationForm(BaseForm):
    token = StringField(
        label='token',
        validators=[
            DataRequired(message='The notification token is required.'),
        ]
    )
