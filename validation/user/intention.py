from validation import BaseForm
from wtforms import StringField
from wtforms.validators import DataRequired


class CircleAcceptForm(BaseForm):
    code = StringField(
        label='code',
        validators=[
            DataRequired(message='The code is required.'),
        ]
    )
