from validation import BaseForm
from wtforms import IntegerField, StringField
from wtforms.validators import DataRequired, NumberRange


class ProfileForm(BaseForm):
    code = StringField(
        label='code',
        validators=[
            DataRequired(
                message='The code is required.'
            ),
        ]
    )

    size = IntegerField(
        label='size',
        validators=[
            DataRequired(
                message='The size is required.'
            ),
            NumberRange(
                message='The size is invalid.',
                min=1,
                max=2,
            )
        ]
    )
