from elasticsearch_dsl import Completion, Document, Keyword


class CircleDocument(Document):
    from_id = Keyword()
    to_id = Keyword()
    photo_id = Keyword()
    name = Completion(
        preserve_separators=False,
        preserve_position_increments=False,
        contexts=[
            {
                'name': 'from_id',
                'type': 'category',
                'path': 'from_id'
            },
            {
                'name': 'to_id',
                'type': 'category',
                'path': 'to_id'
            }
        ]
    )
    username = Completion(
        preserve_separators=False,
        preserve_position_increments=False,
        contexts=[
            {
                'name': 'from_id',
                'type': 'category',
                'path': 'from_id'
            },
            {
                'name': 'to_id',
                'type': 'category',
                'path': 'to_id'
            }
        ]
    )

    class Index:
        name = 'circles-v1'
