import logging
from google.appengine.ext import ndb
from passlib.handlers.pbkdf2 import pbkdf2_sha256

from lib import utils

__author__ = 'faisal'


class BaseModel(ndb.Model):
    """
    Base model
    """
    created = ndb.DateTimeProperty(auto_now_add=True)
    modified = ndb.DateTimeProperty(auto_now=True)

    def to_client(self):

        return self.to_client_async().get_result()

    @ndb.tasklet
    def to_client_async(self):

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


class Auth(ndb.Model):
    user = ndb.IntegerProperty()

    @classmethod
    def create(cls, key, user):
        auth = cls(key=ndb.Key(cls, key), user=user)
        auth.put()


class User(BaseModel):
    email = ndb.StringProperty()
    name = ndb.StringProperty(indexed=False)
    password = ndb.StringProperty(indexed=False)

    @classmethod
    @ndb.transactional(xg=True)
    def register(cls, **kwargs):
        email = kwargs['email'].lower()
        auth = Auth.get_by_id(email)

        if not auth:
            user = cls(name=kwargs['name'],
                       email=kwargs['email'],
                       password=cls.get_password(utils.aes_decrypt(kwargs['password'])))

            user.put()
            Auth.create(email, user.key.id())

            return user

    @classmethod
    @ndb.transactional(xg=True)
    def get_user_by_oauth(cls, result):
        auth_key = '{}-{}'.format(result.provider.__class__.__name__, result.user.id)
        auth = Auth.get_by_id(auth_key)

        if not auth:
            user = cls(name=result.user.name,
                       email=result.user.email)
            user.put()
            Auth.create(auth_key, user.key.id())
            user_key = user.key
        else:
            user_key = ndb.Key(cls, auth.user)

        return user_key.id()

    @classmethod
    def get_user_by_login(cls, email, password):
        email = email.lower()
        auth = Auth.get_by_id(email.lower())

        if auth:
            user = cls.get_by_id(auth.user)
            if user.password and pbkdf2_sha256.verify(password, user.password):
                return user

    @classmethod
    def get_password(cls, password):

        return pbkdf2_sha256.encrypt(password, rounds=config.password_iterations)

    @ndb.tasklet
    def to_client_async(self):

        return {
            'id': self.key.id() if self.key else None,
            'created': utils.to_js_time(self.created),
            'modified': utils.to_js_time(self.modified),
            'name': self.name,
            'email': self.email
        }
