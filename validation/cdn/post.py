from validation import BaseForm
from wtforms import StringField
from wtforms.validators import DataRequired, AnyOf


class PostItemForm(BaseForm):
    code = StringField(
        label='code',
        validators=[
            DataRequired(
                message='The code is required.'
            ),
        ]
    )

    size = StringField(
        label='size',
        validators=[
            DataRequired(
                message='The size is required.'
            ),
            AnyOf(
                message='The size is invalid.',
                values=['thumb', 'large'],
            )
        ]
    )

    hashes = StringField(
        label='hash',
        validators=[
            DataRequired(
                message='The hash is required.'
            ),
        ]
    )

    extension = StringField(
        label='extension',
        validators=[
            DataRequired(
                message='The extension is required.'
            ),
            AnyOf(
                message='The extension is invalid.',
                values=['mp4', 'jpg', 'jpeg'],
            )
        ]
    )
