import logging
from lib.basehandler import RpcHandler
from google.appengine.ext import deferred


class ApiHandler(RpcHandler):

    def user_id(self):

        return self.session.get('user_id', 0)
