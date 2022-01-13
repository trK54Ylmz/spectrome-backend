from validation import BaseForm
from wtforms import StringField
from wtforms.validators import DataRequired, Length


class LocationForm(BaseForm):
    country = StringField(
        label='country',
        validators=[
            DataRequired(
                message='The country code is required.'
            ),
            Length(
                min=2,
                max=2,
                message='The country code is invalid.',
            ),
        ]
    )

    language = StringField(
        label='language',
        validators=[
            DataRequired(
                message='The language code is required.'
            ),
            Length(
                min=2,
                max=10,
                message='The language code is invalid.',
            ),
        ]
    )
