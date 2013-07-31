import logging
from google.appengine.api import oauth
from google.appengine.api.oauth import NotAllowedError
from lib.basehandler import RpcHandler
from google.appengine.ext import deferred
from mappers import demo

ERROR_LOGIN = 'Login Error'
TYPE_ERROR = 'error'


# Sample json rpc, there is not cloud endpoints which helps on easily creating
# clients for your endpoints and versioning. Check handlers/services.py for sample usage
# on how this api handler is converted to cloud endpoints
class ApiHandler(RpcHandler):

    def user_id(self):

        return self.session.get('user_id', 0)

    def login(self):
        # Remember that this is just a sample. You need to get an auth token using whatever
        # client you are logging in to be passed as headers for this to work
        # Header will look like: Authorization: Bearer TokenYouGotHere
        try:
            user = oauth.get_current_user('https://www.googleapis.com/auth/userinfo')
        except NotAllowedError:
            return 0

        if user and user.email():
            self.session['user_id'] = user.user_id()
            return self.session['user_id']

        return 0

    def logout(self):
        if self.is_logged_in():
            del self.session['user_id']
            return True
        return False

    def is_logged_in(self):

        return self.session.get('user_id', 0) != 0

    def hello(self, world, limit=1):

        return [world for i in range(limit)]

    def delete_shouts(self):

        # This sample runs it in the mappers backend, with 100 batches, the more things you do in map
        # the smaller the batch should be to avoid duplicate runs on failures
        deferred.defer(demo.DeleteAllShout().run, 100, _target='mappers')