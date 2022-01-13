from validation import BaseForm
from wtforms import StringField
from wtforms.validators import DataRequired


class UserForm(BaseForm):
    query = StringField(
        label='query',
        validators=[
            DataRequired(
                message='The query is required.'
            ),
        ]
    )
