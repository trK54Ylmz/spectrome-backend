from validation import BaseForm
from wtforms.validators import DataRequired, InputRequired, NumberRange, Length
from wtforms import (
    BooleanField, FieldList, FileField, FloatField, IntegerField, StringField
)


class PostUploadForm(BaseForm):
    files = FieldList(
        FileField(
            label='file',
            validators=[
                DataRequired(
                    message='The post is required.'
                ),
            ]
        ),
        min_entries=1,
        max_entries=10,
    )

    types = FieldList(
        IntegerField(
            label='type',
            validators=[
                DataRequired(
                    message='The type is required.'
                ),
                NumberRange(
                    min=1,
                    max=2,
                    message='Invalid file type selected.'
                ),
            ]
        ),
        min_entries=1,
        max_entries=10,
    )

    scales = FieldList(
        FloatField(
            label='scale',
            validators=[
                DataRequired(
                    message='The scale is required.'
                ),
                NumberRange(
                    min=1,
                    max=4,
                    message='The scale size must be range between 1 and 4.'
                ),
            ]
        ),
        min_entries=1,
        max_entries=10,
    )

    message = StringField(
            label='message',
            validators=[
                DataRequired(
                    message='The message is required.'
                ),
                Length(
                    min=10,
                    max=4000,
                    message='The message length must be between 10 and 4000.'
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
                min=1,
                max=3,
                message='The size must be range between 1 and 3.'
            ),
        ]
    )

    disposable = BooleanField(
        label='disposable',
        false_values=['0'],
        validators=[
            InputRequired(
                message='The disposability selection is required.'
            ),
        ]
    )

    users = FieldList(
        StringField(
            label='user',
            validators=[
                DataRequired(
                    message='The username is required.'
                ),
            ]
        ),
        min_entries=1,
        max_entries=16,
    )
