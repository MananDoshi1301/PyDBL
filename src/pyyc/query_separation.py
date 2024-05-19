class QuerySeparation():

    def __init__(self, query_order):
        self.query_order = query_order
        self.persistence_query = []
        self.non_persistence_query = []
        self.non_persistent_type = ['hset', 'hget']

    def get_persistent_queries(self):
        return self.persistence_query

    def get_non_persistent_queries(self):
        return self.non_persistence_query

    def separate_queries(self):

        for query in self.query_order:
            query_type = query[0]

            if query_type in self.non_persistent_type:
                self.non_persistence_query.append(query)
            else:
                self.persistence_query.append(query)