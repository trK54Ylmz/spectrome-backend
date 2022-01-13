from validation import BaseForm
from validation.custom import Phone
from wtforms import StringField
from wtforms.validators import DataRequired


class PhoneForm(BaseForm):
    phone = StringField(
        label='phone',
        validators=[
            DataRequired(message='The phone number field is required.'),
            Phone(message='The phone number is invalid.')
        ]
    )
