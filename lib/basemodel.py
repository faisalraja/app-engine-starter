from google.appengine.ext import ndb


class BaseModel(ndb.Model):
    """
    Base model
    """
    created = ndb.DateTimeProperty(auto_now_add=True)
    modified = ndb.DateTimeProperty(auto_now=True)

    def to_client(self, **kwargs):

        return self.to_client_async(**kwargs).get_result()

    @ndb.tasklet
    def to_client_async(self, **kwargs):
        """Standardize your client data and use keyword args for adding sensitive data on logged in users"""
        raise ndb.Return(self.to_dict())

    @classmethod
    @ndb.tasklet
    def cached_query_async(cls, qry, cursor=None, limit=10):
        if cursor is not None and not isinstance(cursor, ndb.Cursor):
            cursor = ndb.Cursor(urlsafe=cursor)

        results, cursor, more = yield qry.fetch_page_async(limit, start_cursor=cursor, keys_only=True)
        if results:
            results = ndb.get_multi(results)

        raise ndb.Return(results, cursor, more)
