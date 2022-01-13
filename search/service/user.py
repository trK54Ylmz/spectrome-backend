from search import ElasticService
from search.model import UserDocument


class UserSearchService(ElasticService):
    def complete(self, query):
        """
        Execute user completion suggester

        :param str query: completion suggestion query
        :return: list of suggestion
        :rtype: list[search.model.CircleDocument] or None
        """
        u = UserDocument()

        fu = {
            'field': 'username',
            'size': 10,
        }

        fn = {
            'field': 'name',
            'size': 10,
        }

        # create suggestion query
        s = u.search() \
            .using(self.client) \
            .index(u.Index.name) \
            .suggest('username', query, completion=fu) \
            .suggest('name', query, completion=fn)

        res = s.execute()

        # return null if response is timed out
        if res.timed_out:
            return None

        return res.suggest
