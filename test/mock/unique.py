from validation import BaseForm
from validation.custom import Unique
from wtforms import FieldList, StringField
from wtforms.validators import DataRequired


class UniqueForm(BaseForm):
    items = FieldList(
        unbound_field=StringField(
            label='item',
            validators=[
                DataRequired(message='The item is required.'),
            ]
        ),
        min_entries=1,
        max_entries=3,
        validators=[
            Unique(message='The items must be unique.')
        ]
    )
