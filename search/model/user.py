from elasticsearch_dsl import Completion, Document, Keyword


class UserDocument(Document):
    photo_id = Keyword()
    name = Completion(
        preserve_separators=False,
        preserve_position_increments=False,
    )
    username = Completion(
        preserve_separators=False,
        preserve_position_increments=False,
    )

    class Index:
        name = 'users-v1'
