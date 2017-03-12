import config
from google.appengine.ext import ndb
from lib import utils
from lib import validators
from lib.basemodel import BaseModel
from lib.jsonrpc import ServerException
from lib.validators import ValidationError
from models import User


class Post(BaseModel):
    title = ndb.StringProperty(indexed=False)
    desc = ndb.TextProperty()
    author = ndb.IntegerProperty()

    @classmethod
    def save_post(cls, user, data):

        v = validators.build({
            'title': {'required': True, 'empty': False},
            'desc': {'required': True, 'empty': False}
        })

        if not v.validate(data):
            raise ValidationError(v.errors)

        # todo demo purposes
        if not config.is_local:
            raise ServerException('Disabled on demo page')

        post = cls(author=user,
                   title=data['title'],
                   desc=data['desc'])
        post.put()

        return post

    @classmethod
    def get_recent(cls, cursor=None):
        qry = cls.query().order(-cls.created)

        return cls.cached_query_async(qry, cursor).get_result()

    @ndb.tasklet
    def to_client_async(self, **kwargs):
        # if there are multiple make sure to yield it in groups if possible
        # author, other = yield User.get_by_id_async(self.author), other_async()
        author = yield User.get_by_id_async(self.author)
        author_client = yield author.to_client_async(**kwargs)

        raise ndb.Return({
            'id': self.key.id() if self.key else None,
            'created': utils.to_js_time(self.created),
            'modified': utils.to_js_time(self.modified),
            'title': self.title,
            'desc': self.desc,
            'author': author_client
        })
