from validation import BaseForm
from wtforms import StringField
from wtforms.validators import DataRequired, Optional


class CommentHistoryForm(BaseForm):
    code = StringField(
        label='code',
        validators=[
            DataRequired(
                message='The post code is required.'
            ),
        ]
    )

    timestamp = StringField(
        label='timestamp',
        validators=[
            Optional(),
        ]
    )
