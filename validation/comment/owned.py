from validation import BaseForm
from wtforms import StringField
from wtforms.validators import DataRequired


class OwnedForm(BaseForm):
    code = StringField(
        label='code',
        validators=[
            DataRequired(
                message='The post code is required.'
            ),
        ]
    )
