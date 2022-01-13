from validation import BaseForm
from validation.custom import Unique
from wtforms import FieldList, StringField
from wtforms.validators import DataRequired, Email


class InviteForm(BaseForm):
    email = FieldList(
        unbound_field=StringField(
            label='email',
            validators=[
                DataRequired(message='The e-mail address field is required.'),
                Email(message='The e-mail address is invalid.'),
            ]
        ),
        min_entries=1,
        max_entries=3,
        validators=[
            Unique(message='The e-mail address must be unique.'),
        ]
    )
