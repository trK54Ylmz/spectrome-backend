from search import ElasticService
from search.model import CircleDocument


class CircleSearchService(ElasticService):
    def complete(self, query, from_id):
        """
        Execute circle completion suggester

        :param str query: completion suggestion query
        :param int from_id: target user id
        :return: list of suggestion
        :rtype: list[search.model.CircleDocument] or None
        """
        f = CircleDocument()

        fu = {
            'field': 'username',
            'size': 10,
            'contexts': {
                'from_id': [str(from_id)]
            }
        }

        fn = {
            'field': 'name',
            'size': 10,
            'contexts': {
                'from_id': [str(from_id)]
            }
        }

        # create suggestion query
        s = f.suggest('username', query, completion=fu) \
            .suggest('name', query, completion=fn) \
            .using(self.client) \
            .index(f.Index.name) \
            .search()

        res = s.execute()

        # return null if response is timed out
        if res.timed_out:
            return None

        return res.suggest
