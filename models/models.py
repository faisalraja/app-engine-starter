from google.appengine.ext import ndb

__author__ = 'faisal'


# Put your models here
# or you can group them if it becomes large
class Shout(ndb.Model):
    created = ndb.DateTimeProperty(auto_now_add=True)
    message = ndb.TextProperty()
    # Since this is just a demo you should implement
    # your user stuff your way
    user_id = ndb.StringProperty()

    @classmethod
    def post(cls, message, user_id):
        shout = cls(message=message, user_id=user_id)
        shout.put()
        return shout

    @classmethod
    def list(cls, more_cursor=None):
        qry = cls.query().order(-cls.created)
        # Limit, Start Cursor
        # You can read on my blog on how to handle
        # loading user ids to name asynchronously
        # since you will save your user data differently its simply showing ids
        return qry.fetch_page(5, start_cursor=None if not more_cursor else ndb.Cursor(urlsafe=more_cursor))