from validation import BaseForm
from wtforms import StringField
from wtforms.validators import Optional


class HistoryGetForm(BaseForm):
    timestamp = StringField(
        label='timestamp',
        validators=[
            Optional(),
        ]
    )
