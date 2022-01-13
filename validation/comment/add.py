from validation import BaseForm
from wtforms import StringField
from wtforms.validators import DataRequired, Length


class CommentAddForm(BaseForm):
    code = StringField(
        label='code',
        validators=[
            DataRequired(
                message='The post code is required.'
            ),
        ]
    )

    message = StringField(
        label='message',
        validators=[
            DataRequired(
                message='The message is required.'
            ),
            Length(
                min=2,
                max=1024,
                message='The message should be lower than 2 more than 1024 characters.'
            ),
        ]
    )
