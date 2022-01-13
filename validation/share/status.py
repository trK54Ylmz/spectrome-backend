from validation import BaseForm
from wtforms.validators import DataRequired, Length
from wtforms import StringField


class PostStatusForm(BaseForm):
    code = StringField(
        label='code',
        validators=[
            DataRequired(
                message='The post code is required.'
            ),
            Length(
                message='The post code is invalid.',
                min=32,
                max=40,
            )
        ]
    )
