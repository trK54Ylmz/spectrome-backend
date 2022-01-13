from validation import BaseForm
from wtforms import StringField
from wtforms.validators import Optional


class WaterFallGetForm(BaseForm):
    timestamp = StringField(
        label='timestamp',
        validators=[
            Optional(),
        ]
    )
